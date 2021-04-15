#!/usr/bin/env python
# vim: sw=4 ai expandtab
# Hammurabi game (based on the game HAMURABI by David Ahl
# published in "Basic Computer Games" (C) 1978)
# Copyright 2018, Mitch Patenaude

import random

class Hammurabi(object):

    reign = 10
    food_per_person = 20
    seed_per_acre = 0.5
    acres_per_person = 10

    def __init__(self):
        self.reset()

    def reset(self):
        self.year = 1
        self.population = 100
        self.immigration = 5
        self.starved = 0
        self.total_killed = 0
        self.running_average_killed = 0
        self.acreage = self.population * self.acres_per_person
        self.grain = 2800
        self.eaten_by_rats = 200
        self.bushels_per_acre = 3
        self.land_price = self.newLandPrice()
        self.plague = False
        self.overthrown = False

    def newLandPrice(self):
        return random.randint(17,26)

    def status(self):
        msg = ''
        land_per_person = 1.0 * self.acreage/self.population
        if self.overthrown:
            msg += 'You starved {0} people in one year!\n'.format(self.starved)
            msg += 'Due to this extreme mismanagement, you have not only been\n'
            msg += 'impeached and thrown out of office, but have also been declared\n'
            msg += 'national fink!\n'
        else:
            msg += 'In year {0}, {1} people starved.\n'.format(self.year, self.starved)
            msg += '{0} people came into the city.\n'.format(self.immigration)
            if self.plague:
                msg += 'A horrible plague struck and half the population died!\n'
            msg += 'The city population is now {0}.\n'.format(self.population)
            msg += 'The city now owns {0} acres of land.\n'.format(self.acreage)
            if self.year <= self.reign:
                msg += 'You harvested {0} bushels per acre.\n'.format(self.bushels_per_acre)
                msg += 'Rats ate {0} bushels.\n'.format(self.eaten_by_rats)
                msg += 'You now have {0} bushels in store.\n'.format(self.grain)
                msg += 'Land is trading at {0} bushels per acre.\n'.format(self.land_price)
            else:
                msg += 'You started with {0} acres per person and ended with {1:.2f}\n'.format(self.acres_per_person, land_per_person)
                msg += 'acres per person.  You killed {0} people, or an average\n'.format(self.total_killed)
                msg += 'or {0:.2f} percent of the people per year.\n'.format(self.running_average_killed)
                if land_per_person < .7*self.acres_per_person or self.running_average_killed > 33:
                    msg += 'Due to this extreme mismanagement, you have not only been\n'
                    msg += 'impeached and thrown out of office, but have also been declared\n'
                    msg += 'national fink!\n'
                elif land_per_person < .9*self.acres_per_person or self.running_average_killed > 10:
                    msg += 'Your heavy-handed performance smacks of Nero or Ivan the terrible.\n'
                    msg += 'The (remaining) people find you an unpleasant ruler, and frankly\n'
                    msg += 'hate your guts!\n'
                elif land_per_person < self.acres_per_person or self.running_average_killed > 3:
                    msg += 'Your performance could have been better, but really wasn\'t so bad.\n'
                    msg += '{0} people would dearly like to see you assassinated, but we all\n'.format(random.randint(2, int(self.population*0.8)))
                    msg += 'have our problems.\n'
                else:
                    msg += 'A fantastic performance! Charlemagne and Disraeli could not have done\n'
                    msg += 'better.\n '
                msg += '\nGoodbye Hammurabi!\n'
        return msg

    def run(self, land_bought, food, planted):
        if self.overthrown:
            raise ValueError('You have been impeached,')

        if type(land_bought) is not int or type(food) is not int or type(planted) is not int:
            raise ValueError('Only integer values are accepted for land, food or planting.')

        grain_used = land_bought*self.land_price + food + int(planted*self.seed_per_acre)
        if grain_used > self.grain:
           raise ValueError('Think again Hammurabi, you only have {0} bushels of grain.'.format(self.grain))

        land_available = self.acreage + land_bought
        if land_available < 0:
            raise ValueError('Think again Hammurabi, you cannot sell more land than you own')

        if planted > self.population*self.acres_per_person:
            raise ValueError('But you only have {0} people to tend the fields'.format(self.population))

        if planted > land_available:
            raise ValueError('You only have {0} acres to plant'.format(land_available))

        if self.year > self.reign:
            raise ValueError('Your reign is over')


        # Use up the grain
        self.grain -= grain_used

        # Feed the people
        people_fed = int(food/self.food_per_person)
        self.starved = max(self.population-people_fed, 0) # can't starve a negative amount
        self.total_killed += self.starved

        percent_killed = self.starved*100.0/self.population
        self.running_average_killed = ((self.year-1)*self.running_average_killed + percent_killed)/self.year
        if percent_killed >= 45:
            self.overthrown = True

        # Buy the land
        self.acreage += land_bought

        # Harvest the crops
        self.bushels_per_acre = random.randint(1,5)
        harvest = planted*self.bushels_per_acre

        # Rats run wild
        r = random.randint(1,5)
        if r%2 == 1:
            self.eaten_by_rats = int(self.grain/r)
        else:
            self.eaten_by_rats = 0
        self.grain += harvest - self.eaten_by_rats

        # Have babies
        self.immigration = int(random.randint(1,5)*(20*self.acreage + self.grain)/self.population/100 + 1)
        self.population += self.immigration - self.starved

        # Has there been a plague?
        self.plague = (random.randint(1,20) <= 3) # 15% chance of plague
        if self.plague:
            self.population = int(self.population/2)

        # Set the new price for land
        self.land_price = self.newLandPrice()

        # Start the next year
        self.year += 1


if __name__ == '__main__':
    # autoplay a game to test 
    import argparse

    parser = argparse.ArgumentParser('Rule like Hammurabi')
    parser.add_argument('--reign', default=Hammurabi.reign, type=int,
                        help='How many years should you rule')
    parser.add_argument('--acres-per-person', default=Hammurabi.acres_per_person, type=int,
                        help='How many acres can each person till')
    parser.add_argument('--food-per-person', default=Hammurabi.food_per_person, type=int,
                        help='How much does each person need to eat')
    parser.add_argument('--seed-per-acre', default=Hammurabi.seed_per_acre, type=float,
                        help='How much grain is needed to seed an acre of land')
    args = parser.parse_args()


    Hammurabi.reign = args.reign
    Hammurabi.acres_per_person = args.acres_per_person
    Hammurabi.food_per_person = args.food_per_person
    Hammurabi.seed_per_acre = args.seed_per_acre

    game = Hammurabi()
    # game.reset()
    
    try:
        while game.year <= game.reign and not game.overthrown:
            print(game.status())
            plantable = int(min(game.acreage, game.population*game.acres_per_person))
            if game.grain < (game.population*game.food_per_person + plantable*game.seed_per_acre):
                print('Some people are going to have to do without')
                food = int(game.population*0.95)*game.food_per_person
            else:
                print('Bountiful harvests!')
                food = int(game.population*game.food_per_person)
            land = max(int((game.grain-food-plantable*game.seed_per_acre)/game.land_price), int(-0.5*game.acreage))
            plantable = min(plantable, game.acreage+land)
            food = min(food, int(game.grain - plantable*game.seed_per_acre - land*game.land_price))
            print('land bought: {0}     food: {1}      acreage planted: {2}'.format(land, food, plantable))
            print('')
            game.run(land, food, plantable)
    except Exception as e:
        print(str(e))
    print(game.status())
