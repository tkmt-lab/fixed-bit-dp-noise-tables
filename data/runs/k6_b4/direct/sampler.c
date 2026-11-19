/* Generated. Valid d index and uniform b-bit word are caller preconditions.
 * One address-dependent load; no constant-time guarantee. No RNG inside. */
#include <stdint.h>
static const uint16_t MAP[6][16] = {
{1,1,1,1,1,1,1,1,1,1,3,4,4,4,4,5},
{1,1,1,1,1,1,1,1,1,1,3,4,4,4,4,5},
{1,1,1,1,1,3,3,4,4,4,4,4,4,4,4,5},
{1,1,1,1,1,3,3,4,4,4,4,4,4,4,4,5},
{1,1,1,1,1,3,4,4,4,4,4,4,4,4,5,5},
{1,1,1,1,1,1,1,1,1,3,4,4,4,4,5,5}
};
uint16_t sample_from_bits(uint32_t d, uint32_t word) {
    return MAP[d][word];
}
