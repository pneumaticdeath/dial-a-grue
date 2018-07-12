from cribbage import count_hand, Hand
from cards import Card

def dump(hand, crib_card, is_crib=False, correct_score=None):
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
    if correct_score is not None and s != correct_score:
        print('FAILURE: score = {}, but correct score = {}'.format(s, correct_score))

if __name__ == '__main__':

    crib_card = Card(4, 'hearts')
    hand = Hand([Card(4, 'spades'), Card(5, 'spades'), Card(6, 'spades'), Card(6, 'clubs')])
    dump(hand, crib_card, correct_score=24)

    print('')

    crib_card = Card(1, 'hearts')
    hand = Hand([Card(2, 'spades'), Card(3, 'spades'), Card(5, 'spades'), Card(4, 'clubs')])
    dump(hand, crib_card, correct_score=7)

    print('')

    hand = Hand([Card(2, 'spades'), Card(1, 'spades'), Card(3, 'spades'), Card(4, 'clubs')])
    dump(hand, crib_card, correct_score=10)

    print('')

    hand = Hand([Card(2, 'spades'), Card(1, 'spades'), Card(3, 'spades'), Card(1, 'clubs')])
    dump(hand, crib_card, correct_score=15)

    print('')

    crib_card = Card(5, 'hearts')
    hand = Hand([Card(5, 'spades'), Card(11, 'hearts'), Card(5, 'diamonds'), Card(5, 'clubs')])
    dump(hand, crib_card, correct_score=29)

    print('')

    hand = Hand([Card(5, 'spades'), Card(11, 'spades'), Card(5, 'diamonds'), Card(5, 'clubs')])
    dump(hand, crib_card, correct_score=28)

    print('')

    crib_card = Card(2, 'hearts')
    hand = Hand([Card(4, 'spades'), Card(6,'spades'), Card(8, 'spades'), Card(10, 'spades')])
    dump(hand, crib_card, False, correct_score=4)
    dump(hand, crib_card, True, correct_score=0)
    crib_card = Card(2, 'spades')
    dump(hand, crib_card, False, correct_score=5)
    dump(hand, crib_card, True, correct_score=5)


