/*
 * fileio.c
 *
 * File manipulation routines. Should be generic.
 *
 */

#include "ztypes.h"

/* Static data */

static FILE *gfp = NULL; /* Game file pointer */
static FILE *sfp = NULL; /* Script file pointer */
static FILE *rfp = NULL; /* Record file pointer */
static char save_name[FILENAME_MAX + 1] = "";
static char script_name[FILENAME_MAX + 1] = "";
static char record_name[FILENAME_MAX + 1] = "";

static int undo_valid = FALSE;
static zword_t undo_stack[STACK_SIZE];

static int script_file_valid = FALSE;

static int save_restore (const char *, int);

/*
 * open_story
 *
 * Open game file for read.
 *
 */

void open_story (const char *storyname)
{
    char *path, *p;
    char tmp[PATHNAME_MAX + 1];
    
    if ((gfp = fopen (storyname, "rb")))
       return;

    if ((path = getenv("INFOCOM_PATH")) == NULL)
       fatal ("Can't open game file");
    
    p = strtok(path, ":");
    while (p)
    {
       sprintf (tmp, "%s/%s", p, storyname);
       if ((gfp = fopen (tmp, "rb")))
           return;
       p = strtok(NULL, ":");
    }

    fatal ("Can't open game file");

}/* open_story */

/*
 * close_story
 *
 * Close game file if open.
 *
 */

void close_story (void)
{

    if (gfp != NULL)
        fclose (gfp);

}/* close_story */

/*
 * get_story_size
 *
 * Calculate the size of the game file. Only used for very old games that do not
 * have the game file size in the header.
 *
 */

unsigned int get_story_size (void)
{
    unsigned long file_length;

    /* Read whole file to calculate file size */

    rewind (gfp);
    for (file_length = 0; fgetc (gfp) != EOF; file_length++)
        ;
    rewind (gfp);

    /* Calculate length of file in game allocation units */

    file_length = (file_length + (unsigned long) (story_scaler - 1)) / (unsigned long) story_scaler;

    return ((unsigned int) file_length);

}/* get_story_size */

/*
 * read_page
 *
 * Read one game file page.
 *
 */

void read_page (int page, void *buffer)
{
    unsigned long file_size;
    unsigned int pages, offset;

    /* Seek to start of page */

    fseek (gfp, (long) page * PAGE_SIZE, SEEK_SET);

    /* Read the page */

    if (fread (buffer, PAGE_SIZE, 1, gfp) != 1) {

        /* Read failed. Are we in the last page? */

        file_size = (unsigned long) h_file_size * story_scaler;
        pages = (unsigned int) ((unsigned long) file_size / PAGE_SIZE);
        offset = (unsigned int) ((unsigned long) file_size & PAGE_MASK);
        if ((unsigned int) page == pages) {

            /* Read partial page if this is the last page in the game file */

            fseek (gfp, (long) page * PAGE_SIZE, SEEK_SET);
            if (fread (buffer, offset, 1, gfp) == 1)
                return;
        }
        fatal ("Game file read error");
    }

}/* read_page */

/*
 * verify
 *
 * Verify game ($verify verb). Add all bytes in game file except for bytes in
 * the game file header.
 *
 */

void verify (void)
{
    unsigned long file_size;
    unsigned int pages, offset;
    unsigned int start, end, i, j;
    zword_t checksum = 0;
    zbyte_t buffer[PAGE_SIZE];

    /* Print version banner */

    if (h_type < V4) {
        write_string ("ZIP Interpreter ");
        print_number (get_byte (H_INTERPRETER));
        write_string (", Version ");
        write_char (get_byte (H_INTERPRETER_VERSION));
        write_string (".");
        new_line ();
    }

    /* Calculate game file dimensions */

    file_size = (unsigned long) h_file_size * story_scaler;
    pages = (unsigned int) ((unsigned long) file_size / PAGE_SIZE);
    offset = (unsigned int) file_size & PAGE_MASK;

    /* Sum all bytes in game file, except header bytes */

    for (i = 0; i <= pages; i++) {
        read_page (i, buffer);
        start = (i == 0) ? 64 : 0;
        end = (i == pages) ? offset : PAGE_SIZE;
        for (j = start; j < end; j++)
            checksum += buffer[j];
    }

    /* Make a conditional jump based on whether the checksum is equal */

    conditional_jump (checksum == h_checksum);

}/* verify */

/*
 * save
 *
 * Save game state to disk. Returns:
 *     0 = save failed
 *     1 = save succeeded
 *
 */

int save (void)
{
    char new_save_name[FILENAME_MAX + 1];
    int status = 1;

    /* Get the file name */

    if (get_file_name (new_save_name, save_name, GAME_SAVE) == 0) {

        /* Do a save operation */

        if (save_restore (new_save_name, GAME_SAVE) == 0) {

            /* Cleanup file */

            file_cleanup (new_save_name, GAME_SAVE);

            /* Save the new name as the default file name */

            strcpy (save_name, new_save_name);

            /* Indicate success */

            status = 0;

        }

    }

    /* Return result of save to Z-code */

    if (h_type < V4)
        conditional_jump (status == 0);
    else
        store_operand ((status == 0) ? 1 : 0);

    return (status);

}/* save */

/*
 * restore
 *
 * Restore game state from disk. Returns:
 *     0 = restore failed
 *     2 = restore succeeded
 *
 */

int restore (void)
{
    char new_save_name[FILENAME_MAX + 1];
    int status = 1;

    /* Get the file name */

    if (get_file_name (new_save_name, save_name, GAME_RESTORE) == 0) {

        /* Do the restore operation */

        if (save_restore (new_save_name, GAME_RESTORE) == 0) {

            /* Reset the status region (this is just for Seastalker) */

            if (h_type < V4) {
                set_status_size (0);
                blank_status_line ();
            }

            /* Cleanup file */

            file_cleanup (new_save_name, GAME_SAVE);

            /* Save the new name as the default file name */

            strcpy (save_name, new_save_name);

            /* Indicate success */

            status = 0;

        }

    }

    /* Return result of save to Z-code */

    if (h_type < V4)
        conditional_jump (status == 0);
    else
        store_operand ((status == 0) ? 2 : 0);

    return (status);

}/* restore */

/*
 * undo_save
 *
 * Save the current Z machine state in memory for a future undo. Returns:
 *    -1 = feature unavailable
 *     0 = save failed
 *     1 = save succeeded
 *
 */

void undo_save (void)
{

    /* Check if undo is available first */

    if (undo_datap != NULL) {

        /* Save the undo data and return success */

        save_restore (NULL, UNDO_SAVE);

        undo_valid = TRUE;

        store_operand (1);

    } else 

        /* If no memory for data area then say undo is not available */

        store_operand ((zword_t) -1);

}/* undo_save */

/*
 * undo_restore
 *
 * Restore the current Z machine state from memory. Returns:
 *    -1 = feature unavailable
 *     0 = restore failed
 *     2 = restore succeeded
 *
 */

void undo_restore (void)
{

    /* Check if undo is available first */

    if (undo_datap != NULL) {

        /* If no undo save done then return an error */

        if (undo_valid == TRUE) {

            /* Restore the undo data and return success */

            save_restore (NULL, UNDO_RESTORE);

            store_operand (2);

        } else

            store_operand (0);

    } else 

        /* If no memory for data area then say undo is not available */

        store_operand ((zword_t) -1);

}/* undo_restore */

/*
 * save_restore
 *
 * Common save and restore code. Just save or restore the game stack and the
 * writeable data area.
 *
 */

static int save_restore (const char *file_name, int flag)
{
    FILE *tfp = NULL;
    int scripting_flag = 0, status = 0;

    /* Open the save file and disable scripting */

    if (flag == GAME_SAVE || flag == GAME_RESTORE) {
        if ((tfp = fopen (file_name, (flag == GAME_SAVE) ? "wb" : "rb")) == NULL) {
            output_line ("Cannot open SAVE file");
            return (1);
        }
        scripting_flag = get_word (H_FLAGS) & SCRIPTING_FLAG;
        set_word (H_FLAGS, get_word (H_FLAGS) & (~SCRIPTING_FLAG));
    }

    /* Push PC, FP, version and store SP in special location */

    stack[--sp] = (zword_t) (pc / PAGE_SIZE);
    stack[--sp] = (zword_t) (pc % PAGE_SIZE);
    stack[--sp] = fp;
    stack[--sp] = h_version;
    stack[0] = sp;

    /* Save or restore stack */

    if (flag == GAME_SAVE) {
        if (status == 0 && fwrite (stack, sizeof (stack), 1, tfp) != 1)
            status = 1;
    } else if (flag == GAME_RESTORE) {
        if (status == 0 && fread (stack, sizeof (stack), 1, tfp) != 1)
            status = 1;
    } else if (flag == UNDO_SAVE) {
        memmove (undo_stack, stack, sizeof (stack));
    } else /* if (flag == UNDO_RESTORE) */
        memmove (stack, undo_stack, sizeof (stack));

    /* Restore SP, check version, restore FP and PC */

    sp = stack[0];
    if (stack[sp++] != h_version)
        fatal ("Wrong game or version");
    fp = stack[sp++];
    pc = stack[sp++];
    pc += (unsigned long) stack[sp++] * PAGE_SIZE;

    /* Save or restore writeable game data area */

    if (flag == GAME_SAVE) {
        if (status == 0 && fwrite (datap, h_restart_size, 1, tfp) != 1)
            status = 1;
    } else if (flag == GAME_RESTORE) {
        if (status == 0 && fread (datap, h_restart_size, 1, tfp) != 1)
            status = 1;
    } else if (flag == UNDO_SAVE) {
        memmove (undo_datap, datap, h_restart_size);
    } else /* if (flag == UNDO_RESTORE) */
        memmove (datap, undo_datap, h_restart_size);

    /* Close the save file and restore scripting */

    if (flag == GAME_SAVE || flag == GAME_RESTORE) {
        fclose (tfp);
        if (scripting_flag)
            set_word (H_FLAGS, get_word (H_FLAGS) | SCRIPTING_FLAG);
    }

    /* Handle read or write errors */

    if (status) {
        if (flag == GAME_SAVE) {
            output_line ("Write to SAVE file failed");
            remove (file_name);
        } else {
            output_line ("Read from SAVE file failed");
        }
    }

    return (status);

}/* save_restore */

/*
 * open_script
 *
 * Open the scripting file.
 *
 */

void open_script (void)
{
    char new_script_name[FILENAME_MAX + 1];

    /* Open scripting file if closed */

    if (scripting == OFF) {

        if (script_file_valid == TRUE) {

            sfp = fopen (script_name, "a");

            /* Turn on scripting if open succeeded */

            if (sfp != NULL)
                scripting = ON;
            else
                output_line ("Script file open failed");

        } else {

            /* Get scripting file name and record it */

            if (get_file_name (new_script_name, script_name, GAME_SCRIPT) == 0) {

                /* Open scripting file */

                sfp = fopen (new_script_name, "w");

                /* Turn on scripting if open succeeded */

                if (sfp != NULL) {

                    script_file_valid = TRUE;

                    /* Make file name the default name */

                    strcpy (script_name, new_script_name);

                    /* Turn on scripting */

                    scripting = ON;
            
                } else

                    output_line ("Script file create failed");

            }

        }

    }

    /* Set the scripting flag in the game file flags */

    if (scripting == ON)
        set_word (H_FLAGS, get_word (H_FLAGS) | SCRIPTING_FLAG);
    else
        set_word (H_FLAGS, get_word (H_FLAGS) & (~SCRIPTING_FLAG));

}/* open_script */

/*
 * close_script
 *
 * Close the scripting file.
 *
 */

void close_script (void)
{

    /* Close scripting file if open */

    if (scripting == ON) {

        fclose (sfp);
#if 0
        /* Cleanup */

        file_cleanup (script_name, GAME_SCRIPT);
#endif
        /* Turn off scripting */

        scripting = OFF;

    }

    /* Set the scripting flag in the game file flags */

    // FIXME(mitch): Se just went from ON->OFF in the last element, how can scripting != OFF
    if (scripting == OFF)
        set_word (H_FLAGS, get_word (H_FLAGS) & (~SCRIPTING_FLAG));
    else
        set_word (H_FLAGS, get_word (H_FLAGS) | SCRIPTING_FLAG);

}/* close_script */

/*
 * script_char
 *
 * Write one character to scripting file.
 *
 * Check the state of the scripting flag first. Older games only set the
 * scripting flag in the game flags instead of calling the set_print_modes
 * function. This is because they expect a physically attached printer that
 * doesn't need opening like a file.
 */

void script_char (int c)
{

    /* Check the state of the scripting flag in the game flags. If it is on
       then check to see if the scripting file is open as well */

    if ((get_word (H_FLAGS) & SCRIPTING_FLAG) != 0 && scripting == OFF)
        open_script ();

    /* Check the state of the scripting flag in the game flags. If it is off
       then check to see if the scripting file is closed as well */

    if ((get_word (H_FLAGS) & SCRIPTING_FLAG) == 0 && scripting == ON)
        close_script ();

    /* If scripting file is open, we are in the text window and the character is
       printable then write the character */

    if (scripting == ON && scripting_disable == OFF && (c == '\n' || (isprint (c))))
        putc (c, sfp);

}/* script_char */

/*
 * script_string
 *
 * Write a string to the scripting file.
 *
 */

void script_string (const char *s)
{

    /* Write string */

    while (*s)
        script_char (*s++);

}/* script_string */

/*
 * script_line
 *
 * Write a string followed by a new line to the scripting file.
 *
 */

void script_line (const char *s)
{

    /* Write string */

    script_string (s);

    /* Write new line */

    script_new_line ();

}/* script_line */

/*
 * script_new_line
 *
 * Write a new line to the scripting file.
 *
 */

void script_new_line (void)
{

    script_char ('\n');

}/* script_new_line */

/*
 * open_record
 *
 * Turn on recording of all input to an output file.
 *
 */

void open_record (void)
{
    char new_record_name[FILENAME_MAX + 1];

    /* If recording or playback is already on then complain */

    if (recording == ON || replaying == ON) {

        output_line ("Recording or playback are already active.");

    } else {

        /* Get recording file name */

        if (get_file_name (new_record_name, record_name, GAME_RECORD) == 0) {

            /* Open recording file */

            rfp = fopen (new_record_name, "w");

            /* Turn on recording if open succeeded */

            if (rfp != NULL) {

                /* Make file name the default name */

                strcpy (record_name, new_record_name);

                /* Set recording on */

                recording = ON;

            } else

                output_line ("Record file create failed");

        }

    }

}/* open_record */

/*
 * record_line
 *
 * Write a string followed by a new line to the recording file.
 *
 */

void record_line (const char *s)
{

    if (recording == ON && replaying == OFF) {

        /* Write string */

        fprintf (rfp, "%s\n", s);

    }

}/* record_line */

/*
 * record_key
 *
 * Write a key followed by a new line to the recording file.
 *
 */

void record_key (int c)
{

    if (recording == ON && replaying == OFF) {

        /* Write the key */

        fprintf (rfp, "<%0o>\n", c);

    }

}/* record_key */

/*
 * close_record
 *
 * Turn off recording of all input to an output file.
 *
 */

void close_record (void)
{

    /* Close recording file */

    if (rfp != NULL) {
        fclose (rfp);
        rfp = NULL;

        /* Cleanup */

        if (recording == ON)
            file_cleanup (record_name, GAME_RECORD);
        else /* (replaying == ON) */
            file_cleanup (record_name, GAME_PLAYBACK);
    }

    /* Set recording and replaying off */

    recording = OFF;
    replaying = OFF;

}/* close_record */

/*
 * open_playback
 *
 * Take input from command file instead of keyboard.
 *
 */

void open_playback (int arg)
{
    char new_record_name[FILENAME_MAX + 1];

    /* If recording or replaying is already on then complain */

    if (recording == ON || replaying == ON) {

        output_line ("Recording or replaying is already active.");

    } else {

        /* Get recording file name */

        if (get_file_name (new_record_name, record_name, GAME_PLAYBACK) == 0) {

            /* Open recording file */

            rfp = fopen (new_record_name, "r");

            /* Turn on recording if open succeeded */

            if (rfp != NULL) {

                /* Make file name the default name */

                strcpy (record_name, new_record_name);

                /* Set replaying on */

                replaying = ON;

            } else

                output_line ("Record file open failed");

        }

    }

}/* open_playback */

/*
 * playback_line
 *
 * Get a line of input from the command file.
 *
 */

int playback_line (int buflen, char *buffer, int *read_size)
{
    char *cp;

    if (recording == ON || replaying == OFF)
        return (-1);

    if (fgets (buffer, buflen, rfp) == NULL) {
        close_record ();
        return (-1);
    } else {
        cp = strrchr (buffer, '\n');
        if (cp != NULL)
            *cp = '\0';
        *read_size = strlen (buffer);
        output_line (buffer);
    }

    return ('\n');

}/* playback_line */

/*
 * playback_key
 *
 * Get a key from the command file.
 *
 */

int playback_key (void)
{
    int c;

    if (recording == ON || replaying == OFF)
        return (-1);

    if (fscanf (rfp, "<%o>\n", &c) == EOF) {
        close_record ();
        c = -1;
    }

    return (c);

}/* playback_key */
