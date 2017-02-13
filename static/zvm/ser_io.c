/* unixio.c */

#include "ztypes.h"

#if !defined(BSD) && !defined(SYSTEM_FIVE) && !defined(POSIX)
#error "define one of BSD, SYSTEM_FIVE or POSIX"
#endif /* !defined(BSD) && !defined(SYSTEM_FIVE) && !defined(POSIX) */

#if defined(BSD)
#include <sgtty.h>
#endif /* defined(BSD) */
#if defined(SYSTEM_FIVE)
#include <termio.h>
#endif /* defined(SYSTEM_FIVE) */
#if defined(POSIX)
// #include <termios.h>
#endif /* defined(POSIX) */

#include <signal.h>
#include <sys/types.h>
#include <sys/time.h>

static int current_row = 1;
static int current_col = 1;

static int saved_row;
static int saved_col;

static int cursor_saved = OFF;

// static char tcbuf[1024];
// static char cmbuf[1024];
// static char *cmbufp;

// static char *CE, *CL, *CM, *CS, *DL, *MD, *ME, *MR, *SE, *SO, *TE, *TI, *UE, *US;

// #define GET_TC_STR(p1, p2) if ((p1 = tgetstr (p2, &cmbufp)) == NULL) p1 = ""

// #define BELL '*'

static void outc ();
static void display_string ();
static int wait_for_char ();
static int read_key ();
// static void set_cbreak_mode ();
static void rundown ();
static void tstp_zip ();
static void cont_zip ();

// extern int tgetent ();
// extern int tgetnum ();
// extern char *tgetstr ();
// extern char *tgoto ();
// extern void tputs ();

static void outc (c)
int c;
{

    putchar (c);

}/* outc */

void ring_bell () 
{
    outc((int) 7);
}

void initialize_screen ()
{
    // set_cbreak_mode (1);
    screen_rows=1000;
    screen_cols=1000;

}/* initialize_screen */

void restart_screen ()
{

    cursor_saved = OFF;

    if (h_type < V4)
        set_byte (H_CONFIG, (get_byte (H_CONFIG) | CONFIG_WINDOWS));
    else
        set_byte (H_CONFIG, (get_byte (H_CONFIG) | CONFIG_EMPHASIS | CONFIG_WINDOWS));

    /* Force graphics off as we can't do them */

    set_word (H_FLAGS, (get_word (H_FLAGS) & (~GRAPHICS_FLAG)));

}/* restart_screen */

void reset_screen ()
{

    // delete_status_window ();
    select_text_window ();
    // set_attribute (NORMAL);

    // set_cbreak_mode (0);

}/* reset_screen */

void clear_screen ()
{
    current_row = 1;
    current_col = 1;

}/* clear_screen */

void select_status_window ()
{

    // save_cursor_position ();

}/* select_status_window */

void select_text_window ()
{

    // restore_cursor_position ();

}/* select_text_window */

void create_status_window ()
{

}/* create_status_window */

void delete_status_window ()
{

}/* delete_status_window */

void clear_line ()
{

}/* clear_line */

void clear_text_window ()
{

}/* clear_text_window */

void clear_status_window ()
{

}/* clear_status_window */

// void move_cursor (row, col)
// int row;
// int col;
// {
// 
    // tputs (tgoto (CM, col - 1, row - 1), 1, outc);
    // current_row = row;
    // current_col = col;
// 
// }/* move_cursor */

void get_cursor_position (row, col)
int *row;
int *col;
{

    *row = current_row;
    *col = current_col;

}/* get_cursor_position */

// void save_cursor_position ()
// {
// 
    // if (cursor_saved == OFF) {
        // get_cursor_position (&saved_row, &saved_col);
        // cursor_saved = ON;
    // }

// }/* save_cursor_position */

// void restore_cursor_position ()
// {
//                       
    // if (cursor_saved == ON) {
        // move_cursor (saved_row, saved_col);
        // cursor_saved = OFF;
    // }

// }/* restore_cursor_position */

void set_attribute (attribute)
int attribute;
{

}/* set_attribute */

static void display_string (s)
char *s;
{

    while (*s)
        display_char (*s++);

}/* display_string */

void display_char (c)
int c;
{

    outc (c);

    // if (++current_col > screen_cols)
        // current_col = screen_cols;

}/* display_char */

void scroll_line ()
{
  // outc('\r');
  outc('\n');

}/* scroll_line */

int input_character (timeout)
int timeout;
{
    struct timeval tv;
    struct timezone tz;

    gettimeofday (&tv, &tz);

    tv.tv_sec += timeout;

    fflush (stdout);

    if (timeout && wait_for_char (&tv))
        return (-1);

    return (read_key ());

}/* input_character */

int input_line (buflen, buffer, timeout, read_size)
int buflen;
char *buffer;
int timeout;
int *read_size;
{
    struct timeval tv;
    struct timezone tz;
    int c, row, col;

    gettimeofday (&tv, &tz);

    tv.tv_sec += timeout;

    for ( ; ; ) {

        /* Read a single keystroke */

        fflush (stdout);

        if (timeout && wait_for_char (&tv))
            return (-1);
        c = read_key ();

        if (c == '\b') {

            /* Delete key action */

            if (*read_size == 0) {

                /* Ring bell if line is empty */

                ring_bell();

            } else {

                /* Decrement read count */

                (*read_size)--;

                /* Erase last character typed */

                // get_cursor_position (&row, &col);
                // move_cursor (row, --col);
                // outc('\b');
                // display_char (' ');
                // outc('\b');
            }

        } else {

            /* Normal key action */

            if (*read_size == (buflen - 1)) {

                /* Ring bell if buffer is full */

                ring_bell();

            } else {

                /* Scroll line if return key pressed */

                if (c == '\r') {
                    scroll_line ();
                    return (c);
                } else {

                    /* Put key in buffer and display it */

                    buffer[(*read_size)++] = (char) c;
                    // display_char (c);
                }
            }
        }
    }

}/* input_line */

static int wait_for_char (timeout)
struct timeval *timeout;
{
    int nfds, status;
    fd_set readfds;
    struct timeval tv;
    struct timezone tz;

    gettimeofday (&tv, &tz);

    if (tv.tv_sec >= timeout->tv_sec && tv.tv_usec >= timeout->tv_usec)
        return (-1);

    tv.tv_sec = timeout->tv_sec - tv.tv_sec;
    if (timeout->tv_usec < tv.tv_usec) {
        tv.tv_sec--;
        tv.tv_usec = (timeout->tv_usec + 1000000) - tv.tv_usec;
    } else
        tv.tv_usec = timeout->tv_usec - tv.tv_usec;

    nfds = getdtablesize ();
    FD_ZERO (&readfds);
    FD_SET (fileno (stdin), &readfds);

    status = select (nfds, &readfds, NULL, NULL, &tv);
    if (status < 0) {
        perror ("select");
        return (-1);
    }

    if (status == 0)
        return (-1);
    else
        return (0);

}/* wait_for_char */

static int read_key ()
{
    int c;

    c = getchar ();

    if (c == 127)
        c = '\b';
    else if (c == '\n')
        c = '\r';

    return (c);

}/* read_key */

// static void set_cbreak_mode (mode)
// int mode;
// {
    // int status;
    // static int initialized = 0;
// #if defined(BSD)
    // struct sgttyb new_tty;
    // static struct sgttyb old_tty;
// #endif /* defined(BSD) */
// #if defined(SYSTEM_FIVE)
    // struct termio new_termio;
    // static struct termio old_termio;
// #endif /* defined(SYSTEM_FIVE) */
// #if defined(POSIX)
    // struct termios new_termios;
    // static struct termios old_termios;
// #endif /* defined(POSIX) */

    // /* Don't try to restore terminal settings if they weren't saved first */
    // if (mode == 0 && initialized == 0)
       // return;
    // initialized = mode;
// 
// #if defined(BSD)
    // status = ioctl (fileno (stdin), (mode) ? TIOCGETP : TIOCSETP, &old_tty);
// #endif /* defined(BSD) */
// #if defined(SYSTEM_FIVE)
    // status = ioctl (fileno (stdin), (mode) ? TCGETA : TCSETA, &old_termio);
// #endif /* defined(SYSTEM_FIVE) */
// #if defined(POSIX)
    // if (mode)
        // status = tcgetattr (fileno (stdin), &old_termios);
    // else
        // status = tcsetattr (fileno (stdin), TCSANOW, &old_termios);
// #endif /* defined(POSIX) */
    // if (status) {
        // perror ("ioctl");
        // exit (1);
    // }

    // if (mode) {
        // signal (SIGINT, rundown);
        // signal (SIGTERM, rundown);
        // signal (SIGTSTP, tstp_zip);
    // }
// 
    // if (mode) {
// #if defined(BSD)
        // status = ioctl (fileno (stdin), TIOCGETP, &new_tty);
// #endif /* defined(BSD) */
// #if defined(SYSTEM_FIVE)
        // status = ioctl (fileno (stdin), TCGETA, &new_termio);
// #endif /* defined(SYSTEM_FIVE) */
// #if defined(POSIX)
        // status = tcgetattr (fileno (stdin), &new_termios);
// #endif /* defined(POSIX) */
        // if (status) {
            // perror ("ioctl");
            // exit (1);
        // }
// 
// #if defined(BSD)
        // new_tty.sg_flags |= CBREAK;
        // new_tty.sg_flags &= ~ECHO;
// #endif /* defined(BSD) */
// #if defined(SYSTEM_FIVE)
        // new_termio.c_lflag &= ~(ICANON | ECHO);
// #endif /* defined(SYSTEM_FIVE) */
// #if defined(POSIX)
        // new_termios.c_lflag &= ~(ICANON | ECHO);
// #endif /* defined(POSIX) */
// 
// #if defined(BSD)
        // status = ioctl (fileno (stdin), TIOCSETP, &new_tty);
// #endif /* defined(BSD) */
// #if defined(SYSTEM_FIVE)
        // status = ioctl (fileno (stdin), TCSETA, &new_termio);
// #endif /* defined(SYSTEM_FIVE) */
// #if defined(POSIX)
        // status = tcsetattr (fileno (stdin), TCSANOW, &new_termios);
// #endif /* defined(POSIX) */
        // if (status) {
            // perror ("ioctl");
            // exit (1);
        // }
    // }
// 
    // if (mode == 0) {
        // signal (SIGINT, SIG_DFL);
        // signal (SIGTERM, SIG_DFL);
        // signal (SIGTSTP, SIG_DFL);
    // }
// 
// }/* set_cbreak_mode */

static void rundown ()
{

    unload_cache ();
    close_story ();
    close_script ();
    reset_screen ();

}/* rundown */

// static void tstp_zip ()
// {
    // reset_screen ();
    // signal (SIGTSTP, SIG_DFL);
    // signal (SIGCONT, cont_zip);
    // raise (SIGTSTP);
// 
// }/* tstp_zip */

// static void cont_zip ()
// {
    // signal (SIGINT, rundown);
    // signal (SIGTERM, rundown);
    // signal (SIGTSTP, tstp_zip);
    // clear_screen ();
    // restart_screen ();
    // set_cbreak_mode ();
// 
// }/* cont_zip */
