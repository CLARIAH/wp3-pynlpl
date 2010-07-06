#---------------------------------------------------------------
# PyNLPl - Data Types
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Based in large part on MIT licensed code from
#    AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
#    Peter Norvig
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

"""This library contains various extra data types, based to a certain extend on MIT-licensed code from Peter Norvig, AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html"""


import bisect

class Queue: #from AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
    """Queue is an abstract class/interface. There are three types:
        Python List: A Last In First Out Queue (no Queue object necessary).
        FIFOQueue(): A First In First Out Queue.
        PriorityQueue(lt): Queue where items are sorted by lt, (default <).
    Each type supports the following methods and functions:
        q.append(item)  -- add an item to the queue
        q.extend(items) -- equivalent to: for item in items: q.append(item)
        q.pop()         -- return the top item from the queue
        len(q)          -- number of items in q (also q.__len())."""

    def extend(self, items):
        """Append all elements from items to the queue"""
        for item in items: self.append(item)

    
#note: A Python list is a LIFOQueue / Stack

class FIFOQueue(Queue): #adapted from AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
    """A First-In-First-Out Queue"""
    def __init__(self, data = []):
        self.data = data
        self.start = 0

    def append(self, item):
        self.data.append(item)

    def __len__(self):
        return len(self.data) - self.start

    def extend(self, items):
        """Append all elements from items to the queue"""
        self.data.extend(items)

    def pop(self):
        """Retrieve the next element in line, this will remove it from the queue"""
        e = self.data[self.start]
        self.start += 1
        if self.start > 5 and self.start > len(self.data)/2:
            self.data = self.data[self.start:]
            self.start = 0
        return e

class PriorityQueue(Queue): #Heavily adapted/extended, originally from AI: A Modern Appproach : http://aima.cs.berkeley.edu/python/utils.html
    """A queue in which the maximum (or minumum) element is returned first, 
    as determined by either an external score function f (by default calling
    the objects score() method). If minimize=True, the item with minimum f(x) is
    returned first; otherwise is the item with maximum f(x) or x.score().


    blockworse can be set to true if you want to prohibit adding worse-scoring items to the queue.
    blockequal can be set to false if you also want to prohibit adding equally-scoring items to the queue.
    (Both parameters default to False)
    """
    def __init__(self, data =[], f = lambda x: x.score, minimize=False, blockworse=False, blockequal=False):
        self.data = []
        self.f = f
        self.minimize=minimize
        self.blockworse=blockworse
        self.blockequal=blockequal
        self.bestscore = None
        for item in data:
            self.append(item)

    def append(self, item):
        """Adds an item to the priority queue (in the right place), returns True if successfull, False if the item was blocked (because of a bad score)"""
        f = self.f(item)
        if callable(f):
            score = f()
        else:
            score = f

        if self.blockworse and self.bestscore != None:
            if self.minimize:
                if score > self.bestscore:
                    return False
            else:
                if score < self.bestscore:
                    return False
        if self.blockequal and self.bestscore != None:
            if self.bestscore == score:
                return False
        if (self.bestscore == None) or (self.minimize and score < self.bestscore) or (not self.minimize and score > self.bestscore):
            self.bestscore = score
        bisect.insort(self.data, (score, item))
        return True

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        """Iterate over all items, in order from best to worst!"""
        if self.minimize: 
            f = lambda x: x
        else:
            f = reversed
        for score, item in f(self.data):
            yield item

    def __getitem__(self, i):
        """Item 0 is always the best item!"""
        if isinstance(i, slice):
            indices = i.indices(len(self))
            if self.minimize:
                return PriorityQueue([ self.data[j][1] for j in range(*indices) ],self.f, self.minimize, self.blockworse, self.blockequal)
            else:
                return PriorityQueue([ self.data[(-1 * j) - 1][1] for j in range(*indices) ],self.f, self.minimize, self.blockworse, self.blockequal)
        else:
            if self.minimize:
                return self.data[i][1]
            else:   
                return self.data[(-1 * i) - 1][1]

    def pop(self):
        """Retrieve the next element in line, this will remove it from the queue"""
        if self.minimize:
            return self.data.pop(0)[1]
        else:
            return self.data.pop()[1]


    def score(self, i):
        """Return the score for item x (cheap lookup), Item 0 is always the best item"""
        if self.minimize:
            return self.data[i][0]
        else:
            return self.data[(-1 * i) - 1][0]

    def prune(self, n):
        """prune all but the first (=best) n items"""
        if self.minimize:
            self.data = self.data[:n]
        else:
            self.data = self.data[-1 * n:]

    def prunebyscore(self, score, retainequalscore=False):
        """Deletes all items below/above a certain score from the queue, depending on whether minimize is True or False. Note: It is recommended (more efficient) to use blockworse=True / blockequal=True instead! Preventing the addition of 'worse' items."""
        if retainequalscore:
            if self.minimize:
                f = lambda x: x[0] <= score
            else:
                f = lambda x: x[0] >= score
        else:
            if self.minimize:
                f = lambda x: x[0] < score
            else:
                f = lambda x: x[0] > score
        self.data = filter(f, self.data)

    def __eq__(self, other):
        return (self.data == other.data) and (self.minimize == other.minimize)


    def __repr__(self):
        return repr(self.data)

    def __add__(self, other):
        """Priority queues can be added up, as long as they all have minimize or maximize (rather than mixed)"""
        assert (isinstance(other, PriorityQueue) and self.minimize == other.minimize)
        return PriorityQueue(self.data + other.data, self.f, self.minimize, self.blockworse, self.blockequal)
