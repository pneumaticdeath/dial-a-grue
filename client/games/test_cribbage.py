from cribbage import count_hand, Hand
from cards import Card, Deck

def dump(hand, crib_card, is_crib=False):
    print('crib card: {:20s} {}: {:60s}'.format(
        crib_card,
        'crib' if is_crib else 'hand',
        hand))
    s, m = count_hand(hand, crib_card, is_crib)
    print('Score: {}'.format(s))
    for x, y, z in m:
        if y is not None:
            print('{} of {} for {}'.format(x, y, z))
        else:
            print('{} for {}'.format(x, z))

if __name__ == '__main__':

    crib_card = Card(4, 'hearts')
    hand = Hand([Card(4, 'spades'), Card(5, 'spades'), Card(6, 'spades'), Card(6, 'clubs')])
    dump(hand, crib_card)

    print('')

    crib_card = Card(1, 'hearts')
    hand = Hand([Card(2, 'spades'), Card(3, 'spades'), Card(5, 'spades'), Card(4, 'clubs')])
    dump(hand, crib_card)

    print('')

    hand = Hand([Card(2, 'spades'), Card(1, 'spades'), Card(3, 'spades'), Card(4, 'clubs')])
    dump(hand, crib_card)

    print('')

    hand = Hand([Card(2, 'spades'), Card(1, 'spades'), Card(3, 'spades'), Card(1, 'clubs')])
    dump(hand, crib_card)

    print('')

    crib_card = Card(5, 'hearts')
    hand = Hand([Card(5, 'spades'), Card(11, 'hearts'), Card(5, 'diamonds'), Card(5, 'clubs')])
    dump(hand, crib_card)

    print('')

    hand = Hand([Card(5, 'spades'), Card(11, 'spades'), Card(5, 'diamonds'), Card(5, 'clubs')])
    dump(hand, crib_card)

    print('')

    crib_card = Card(2, 'hearts')
    hand = Hand([Card(4, 'spades'), Card(6,'spades'), Card(8, 'spades'), Card(10, 'spades')])
    dump(hand, crib_card, False)
    dump(hand, crib_card, True)
    crib_card = Card(2, 'spades')
    dump(hand, crib_card, False)
    dump(hand, crib_card, True)


