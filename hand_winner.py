from dependencies import *

# value of a card is 0 for a 2, all the way up to 12 for an ace
# if a ourHand or oppHand list has more than 2 cards in it, it means that
#        the first 2 are in the actual hand, and the rest are on the table

def drawCards(takenCards=list(),numCards=-69):
    if numCards == -69:#   if the number of cards wanted was not specified, then return
        numCards = 9 - len(takenCards)# as many cards as needed to bring the total to 9

    # draw numCards cards from a deck, not including ones in takenCards
    # deck is global variable stored in dependencies.py
    new_deck = deepcopy(deck)
    for card in takenCards:
        new_deck.remove(card)
    return random.sample(new_deck, numCards)


def evaluateWinner(ourHand,oppHand):
    def compareTwoLists(list1,list2):# returns 1 if first hand wins, 0 if second hand wins, 2 if they are the same
        ### list1 and list2 have to be of type list
        list1 = np.array(sorted(list1,reverse=True))# create sorted np.array of the lists
        list2 = np.array(sorted(list2,reverse=True))

        diffs = list1 - list2# look at differences in our and opponents hands
        for ii,difference in enumerate(diffs):#       starting with each of our highest cards, find the first time someone
            if ii == 5:
                return 2# at this point we have looked at top 5 cards already, and it is a tie
            if difference > 0:#         has a better card
                return 1
            elif difference < 0:
                return 0
        return 2# if no one has a higher card after looking at all 5 pairs, return 2 (indicating tie)
    # ourHand is a list of dicts, with one dict for each card in our hand
    # ourHand and opponentHand are both lists of size 2-7, with exactly two
    # common cards among the two lists. This function will evaluate the best
    # poker hand in each, and return 1 if ourHand beats opponentHand, and 0
    # if opponentHand beats ourHand. Returns 2 if it's a tie

    # This function is implemented as follows. It is split into 7 sections:
    # 1: find high card of both hands
    # 2: find all pairs in both hands
    # 3: find all triples in both hands
    # 4: find all straights in both hands
    # 5: find all flushes in both hands
    # 6: find all full houses in both hands (calculated from 2. and 3.)
    # 7: find all four-of-a-kinds in both hands
    
    # then it evaluates which hand is better

    # this part finds the highest 5 cards in both hands
    highCardWinner = 2
    ourHighCards = [ourHand[1]["value"]]
    for card in ourHand:
        if len(ourHighCards) <= 5:
            ourHighCards.append(card["value"])
        else:
            if card["value"] > min(ourHighCards):
                ourHighCards.remove(min(ourHighCards))
                ourHighCards.append(card["value"])
    
    oppHighCards = [oppHand[1]["value"]]
    for card in oppHand:
        if len(oppHighCards) <= 5:
            oppHighCards.append(card["value"])
        else:
            if card["value"] > min(oppHighCards):
                oppHighCards.remove(min(oppHighCards))
                oppHighCards.append(card["value"])
    highCardWinner = compareTwoLists(ourHighCards,oppHighCards)
    ###########################

    
    # now find pairs, trips, and four-of-a-kinds
    # make a matrix with 13 elements, each element will hold the number of 
    # cards in our hand that has that value
    ourHandMatrix = np.matrix('0,0,0,0,0,0,0,0,0,0,0,0,0')
    oppHandMatrix = np.matrix('0,0,0,0,0,0,0,0,0,0,0,0,0')
    for card in ourHand:
        ourHandMatrix[0,card["value"]-2] = ourHandMatrix[0,card["value"]-2] + 1
    for card in oppHand:
        oppHandMatrix[0,card["value"]-2] = oppHandMatrix[0,card["value"]-2] + 1

    ourPairs = list()
    oppPairs = list()
    ourTrips = list()
    oppTrips = list()
    ourFours = list()
    oppFours = list()
    for ii in range(13):
        if ourHandMatrix[0,ii] == 2:# check for pair
            ourPairs.append(ii)
        if oppHandMatrix[0,ii] == 2:
            oppPairs.append(ii)
        
        if ourHandMatrix[0,ii] == 3:# check for triple
            ourTrips.append(ii)
        if oppHandMatrix[0,ii] == 3:
            oppTrips.append(ii)
        
        if ourHandMatrix[0,ii] == 4:# check for four of a kind
            ourFours.append(ii)
        if oppHandMatrix[0,ii] == 4:
            oppFours.append(ii)
    
    # now fill in the pair and trips lists with -69 until length = 13
    while len(ourPairs) < 13:
        ourPairs.append(-69)
    while len(oppPairs) < 13:
        oppPairs.append(-69)
    while len(ourTrips) < 13:
        ourTrips.append(-69)
    while len(oppTrips) < 13:
        oppTrips.append(-69)
    while len(ourFours) < 13:
        ourFours.append(-69)
    while len(oppFours) < 13:
        oppFours.append(-69)
    pairsWinner = compareTwoLists(ourPairs,oppPairs)
    tripsWinner = compareTwoLists(ourTrips,oppTrips)
    foursWinner = compareTwoLists(ourFours,oppFours)
    ###########################


    # now find straights
    def doesThisStartAStraight(index,matrix):# takes in an index and a np.matrix
        for ii in range(5):
            if index > 8:
                return 0
            if matrix[0,index+ii] == 0:
                return 0
        return 1
    
    straightWinner = 2
    ourBestStraight = -69# stores the low card in our straight, if any
    oppBestStraight = -69# stores the low card in opponent straight, if any
    for ii in range(13):
        if doesThisStartAStraight(ii,ourHandMatrix):
            ourBestStraight = ii
        if doesThisStartAStraight(ii,oppHandMatrix):
            oppBestStraight = ii
    if ourBestStraight > oppBestStraight:
        straightWinner = 1
    if ourBestStraight < oppBestStraight:
        straightWinner = 0
    ###########################



    # now find flushes
    flushWinner = 2
    ourSuits = {    "heart": 0,# create dictionaries that store how many of each suit
                    "diamond": 0,#                                       a hand has
                    "spade": 0,
                    "club": 0    }
    oppSuits = {    "heart": 0,
                    "diamond": 0,
                    "spade": 0,
                    "club": 0    }
    for card in ourHand:# update the number of suits that each hand has
        ourSuits[card["suit"]] = ourSuits[card["suit"]] + 1
    for card in oppHand:
        oppSuits[card["suit"]] = oppSuits[card["suit"]] + 1
    ourFlush = -69
    oppFlush = -69
    if ourSuits["heart"] >= 5 or ourSuits["diamond"] >= 5 or ourSuits["spade"] >= 5 or ourSuits["club"] >= 5:
        ourFlush = 1
    if oppSuits["heart"] >= 5 or oppSuits["diamond"] >= 5 or oppSuits["spade"] >= 5 or oppSuits["club"] >= 5:
        oppFlush = 1
    
    if ourFlush == 1 and oppFlush == -69:
        flushWinner = 1
    if ourFlush == -69 and oppFlush == 1:
        flushWinner = 0
    ###########################




    # now find full houses
    ourFullHouse = -69
    oppFullHouse = -69
    if sum(ourPairs) > (-13*69) and sum(ourTrips) > (-13*69):
        ourFullHouse = max(ourTrips)
    if sum(oppPairs) > (-13*69) and sum(oppPairs) > (-13*69):
        oppFullHouse = max(oppTrips)
    fullHouseWinner = 2
    if ourFullHouse > oppFullHouse:
        fullHouseWinner = 1
    if ourFullHouse < oppFullHouse:
        fullHouseWinner = 0
    ###########################


    # check for royal flush
    ourRoyalFlush = -69
    oppRoyalFlush = -69
    suits = ["heart","diamond","spade","club"]
    for suit in suits:
        royalFlushThisSuit = 1
        for ii in range(8,13):#
            if {"value": ii,    "suit": suit} not in ourHand:
                royalFlushThisSuit = 0
                break
        if royalFlushThisSuit == 1:
            ourRoyalFlush = 1
            break
    for suit in suits:
        royalFlushThisSuit = 1
        for ii in range(8,13):#
            if {"value": ii,    "suit": suit} not in oppHand:
                royalFlushThisSuit = 0
                break
        if royalFlushThisSuit == 1:
            oppRoyalFlush = 1
            break
    
    royalFlushWinner = 2
    if ourRoyalFlush == 1 and oppRoyalFlush == -69:
        royalFlushWinner = 1
    if ourRoyalFlush == -69 and oppRoyalFlush == 1:
        royalFlushWinner = 0
    ###########################


    winners = [royalFlushWinner, foursWinner,
                        fullHouseWinner, flushWinner,
                        straightWinner, tripsWinner,
                        pairsWinner, highCardWinner ]

    for ii in range(len(winners)):
        if winners[ii] != 2:
            return winners[ii]
    return 2

def calculateStrengthOfHand(ourHand,nSims=2000):
    numberOfWins = 0
    for ii in range(nSims):
        if len(ourHand) != 7:# if we haven't seen all 5 cards on the table, we also need to
                             # simulate drawing them
            otherCards = drawCards(takenCards=ourHand,numCards=(7-len(ourHand)))
        else:
            otherCards = list()
        oppHand = drawCards(takenCards=(ourHand+otherCards),numCards=2)
        ourNewHand = ourHand + otherCards
        oppHand = oppHand + ourNewHand[2:7]

        if evaluateWinner(ourNewHand,oppHand) == 1:
            numberOfWins = numberOfWins + 1
    return float(numberOfWins)/float(nSims)
