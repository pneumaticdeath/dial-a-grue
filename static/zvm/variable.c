/*
 * variable.c
 *
 * Variable manipulation routines
 *
 */

#include "ztypes.h"

/*
 * load
 *
 * Load and store a variable value.
 *
 */

void load (zword_t variable)
{

    store_operand (load_variable (variable));

}/* load */

/*
 * push_var
 *
 * Push a value onto the stack
 *
 */

void push_var (zword_t value)
{

    stack[--sp] = value;

}/* push_var */

/*
 * pop_var
 *
 * Pop a variable from the stack.
 *
 */

void pop_var (zword_t variable)
{

    store_variable (variable, stack[sp++]);

}/* pop_var */

/*
 * increment
 *
 * Increment a variable.
 *
 */

void increment (zword_t variable)
{

    store_variable (variable, load_variable (variable) + 1);

}/* increment */

/*
 * decrement
 *
 * Decrement a variable.
 *
 */

void decrement (zword_t variable)
{

    store_variable (variable, load_variable (variable) - 1);

}/* decrement */

/*
 * increment_check
 *
 * Increment a variable and then check its value against a target.
 *
 */

void increment_check (zword_t variable, zword_t target)
{
    short value;

    value = (short) load_variable (variable);
    store_variable (variable, ++value);
    conditional_jump (value > (short) target);

}/* increment_check */

/*
 * decrement_check
 *
 * Decrement a variable and then check its value against a target.
 *
 */

void decrement_check (zword_t variable, zword_t target)
{
    short value;

    value = (short) load_variable (variable);
    store_variable (variable, --value);
    conditional_jump (value < (short) target);

}/* decrement_check */
