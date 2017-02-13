/*
 * math.c
 *
 * Arithmetic, compare and logical instructions
 *
 */

#include "ztypes.h"

/*
 * add
 *
 * Add two operands
 *
 */

void add (zword_t a, zword_t b)
{

    store_operand (a + b);

}/* add */

/*
 * subtract
 *
 * Subtract two operands
 *
 */

void subtract (zword_t a, zword_t b)
{

    store_operand (a - b);

}/* subtract */

/*
 * multiply
 *
 * Multiply two operands
 *
 */

void multiply (zword_t a, zword_t b)
{

    store_operand (a * b);

}/* multiply */

/*
 * divide
 *
 * Divide two operands
 *
 */

void divide (zword_t a, zword_t b)
{

    store_operand (a / b);

}/* divide */

/*
 * zremainder
 *
 * Modulus divide two operands
 *
 */

void zremainder (zword_t a, zword_t b)
{

    store_operand (a % b);

}/* zremainder */

/*
 * shift
 *
 * Shift +/- n bits
 *
 */

void shift (zword_t a, zword_t b)
{

    if ((short) b > 0)
        store_operand (a << (short) b);
    else
        store_operand (a >> abs ((short) b));

}/* shift */


/*
 * arith_shift
 *
 * Aritmetic shift +/- n bits
 *
 */

void arith_shift (zword_t a, zword_t b)
{

    if ((short) b > 0)
        store_operand (a << (short) b);
    else
        if ((short) a > 0)
            store_operand (a >> abs ((short) b));
        else
            store_operand (~((~a) >> abs ((short) b)));

}/* arith_shift */

/*
 * or
 *
 * Logical OR
 *
 */

void or (zword_t a, zword_t b)
{

    store_operand (a | b);

}/* or */

/*
 * not
 *
 * Logical NOT
 *
 */

void not (zword_t a)
{

    store_operand (~a);

}/* not */

/*
 * and
 *
 * Logical AND
 *
 */

void and (zword_t a, zword_t b)
{

    store_operand (a & b);

}/* and */

/*
 * zip_random
 *
 * Return random number between 1 and operand
 *
 */

void zip_random (zword_t a)
{

    if (a == 0)
        store_operand (0);
    else if (a & 0x8000) { /* (a < 0) - used to set seed with #RANDOM */
        srand ((unsigned int) abs (a));
        store_operand (0);
    } else /* (a > 0) */
        store_operand (((zword_t) rand () % a) + 1);

}/* zip_random */

/*
 * test
 *
 * Jump if operand 2 bit mask not set in operand 1
 *
 */

void test (zword_t a, zword_t b)
{

    conditional_jump (((~a) & b) == 0);

}/* test */

/*
 * compare_zero
 *
 * Compare operand against zero
 *
 */

void compare_zero (zword_t a)
{

    conditional_jump (a == 0);

}/* compare_zero */

/*
 * compare_je
 *
 * Jump if operand 1 is equal to any other operand
 *
 */

void compare_je (int count, zword_t *operand)
{
    int i;

    for (i = 1; i < count; i++)
        if (operand[0] == operand[i]) {
            conditional_jump (TRUE);
            return;
        }
    conditional_jump (FALSE);

}/* compare_je */

/*
 * compare_jl
 *
 * Jump if operand 1 is less than operand 2
 *
 */

void compare_jl (zword_t a, zword_t b)
{

    conditional_jump ((short) a < (short) b);

}/* compare_jl */

/*
 * compare_jg
 *
 * Jump if operand 1 is greater than operand 2
 *
 */

void compare_jg (zword_t a, zword_t b)
{

    conditional_jump ((short) a > (short) b);

}/* compare_jg */
