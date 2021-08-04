#  Copyright (C)  2021 Rage Uday Kiran
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
from abstract import *
minSup = float()
finalPatterns = {}


class Item:
    """
    A class used to represent the item with probability in transaction of dataset

    ...

    Attributes:
    __________
        item : int or word
            Represents the name of the item
        probability : float
            Represent the existential probability(likelihood presence) of an item
    """

    def __init__(self, item, probability):
        self.item = item
        self.probability = probability


class Node(object):
    """
    A class used to represent the node of frequentPatternTree

        ...

    Attributes:
    ----------
        item : int
            storing item of a node
        probability : int
            To maintain the expected support of node
        parent : node
            To maintain the parent of every node
        children : list
            To maintain the children of node

    Methods:
    -------

        addChild(itemName)
            storing the children to their respective parent nodes
    """

    def __init__(self, item, children):
        self.item = item
        self.probability = 1
        self.children = children
        self.parent = None

    def addChild(self, node):
        self.children[node.item] = node
        node.parent = self


class Tree(object):
    """
    A class used to represent the frequentPatternGrowth tree structure

    ...

    Attributes:
    ----------
        root : Node
            Represents the root node of the tree
        summaries : dictionary
            storing the nodes with same item name
        info : dictionary
            stores the support of items


    Methods:
    -------
        addTransaction(transaction)
            creating transaction as a branch in frequentPatternTree
        addConditionalPattern(prefixPaths, supportOfItems)
            construct the conditional tree for prefix paths
        conditionalPatterns(Node)
            generates the conditional patterns from tree for specific node
        conditionalTransactions(prefixPaths,Support)
            takes the prefixPath of a node and support at child of the path and extract the frequent items from
            prefixPaths and generates prefixPaths with items which are frequent
        remove(Node)
            removes the node from tree once after generating all the patterns respective to the node
        generatePatterns(Node)
            starts from the root node of the tree and mines the frequent patterns

    """

    def __init__(self):
        self.root = Node(None, {})
        self.summaries = {}
        self.info = {}

    def addTransaction(self, transaction):
        """adding transaction into tree

            :param transaction : it represents the one self.Database in database

            :type transaction : list
        """

        currentNode = self.root
        for i in range(len(transaction)):
            if transaction[i].item not in currentNode.children:
                newNode = Node(transaction[i].item, {})
                l1 = i - 1
                l = []
                while l1 >= 0:
                    l.append(transaction[l1].probability)
                    l1 -= 1
                if len(l) == 0:
                    newNode.probability = transaction[i].probability
                else:
                    newNode.probability = max(l) * transaction[i].probability
                currentNode.addChild(newNode)
                if transaction[i].item in self.summaries:
                    self.summaries[transaction[i].item].append(newNode)
                else:
                    self.summaries[transaction[i].item] = [newNode]
                currentNode = newNode
            else:
                currentNode = currentNode.children[transaction[i].item]
                l1 = i - 1
                l = []
                while l1 >= 0:
                    l.append(transaction[l1].probability)
                    l1 -= 1
                if len(l) == 0:
                    currentNode.probability += transaction[i].probability
                else:
                    currentNode.probability += max(l) * transaction[i].probability

    def addConditionalPattern(self, transaction, sup):
        """constructing conditional tree from prefixPaths

            :param transaction : it represents the one self.Database in database

            :type transaction : list

            :param sup : support of prefixPath taken at last child of the path

            :type sup : int
        """

        # This method takes transaction, support and constructs the conditional tree
        currentNode = self.root
        for i in range(len(transaction)):
            if transaction[i] not in currentNode.children:
                newNode = Node(transaction[i], {})
                newNode.probability = sup
                currentNode.addChild(newNode)
                if transaction[i] in self.summaries:
                    self.summaries[transaction[i]].append(newNode)
                else:
                    self.summaries[transaction[i]] = [newNode]
                currentNode = newNode
            else:
                currentNode = currentNode.children[transaction[i]]
                currentNode.probability += sup

    def conditionalPatterns(self, alpha):
        """generates all the conditional patterns of respective node

            :param alpha : it represents the Node in tree

            :type alpha : Node
        """

        # This method generates conditional patterns of node by traversing the tree
        finalPatterns = []
        sup = []
        for i in self.summaries[alpha]:
            s = i.probability
            set2 = []
            while i.parent.item is not None:
                set2.append(i.parent.item)
                i = i.parent
            if len(set2) > 0:
                set2.reverse()
                finalPatterns.append(set2)
                sup.append(s)
        finalPatterns, support, info = self.conditionalTransactions(finalPatterns, sup)
        return finalPatterns, support, info

    def removeNode(self, nodeValue):
        """removing the node from tree

            :param nodeValue : it represents the node in tree

            :type nodeValue : node
        """

        for i in self.summaries[nodeValue]:
            del i.parent.children[nodeValue]

    def conditionalTransactions(self, condPatterns, support):
        """ It generates the conditional patterns with frequent items

                :param condPatterns : conditionalPatterns generated from conditionalPattern method for respective node

                :type condPatterns : list

                :support : the support of conditional pattern in tree

                :support : int
        """

        global minSup
        pat = []
        sup = []
        count = {}
        for i in range(len(condPatterns)):
            for j in condPatterns[i]:
                if j in count:
                    count[j] += support[i]
                else:
                    count[j] = support[i]
        updatedDict = {}
        updatedDict = {k: v for k, v in count.items() if v >= minSup}
        count = 0
        for p in condPatterns:
            p1 = [v for v in p if v in updatedDict]
            trans = sorted(p1, key=lambda x: updatedDict[x], reverse=True)
            if len(trans) > 0:
                pat.append(trans)
                sup.append(support[count])
                count += 1
        return pat, sup, updatedDict

    def generatePatterns(self, prefix):
        """generates the patterns

            :param prefix : forms the combination of items

            :type prefix : list
        """

        global finalPatterns, minSup
        for i in sorted(self.summaries, key=lambda x: (self.info.get(x))):
            pattern = prefix[:]
            pattern.append(i)
            s = 0
            for x in self.summaries[i]:
                s += x.probability
            if s >= minSup:
                finalPatterns[tuple(pattern)] = self.info[i]
                patterns, support, info = self.conditionalPatterns(i)
                conditionalTree = Tree()
                conditionalTree.info = info.copy()
                for pat in range(len(patterns)):
                    conditionalTree.addConditionalPattern(patterns[pat], support[pat])
                if len(patterns) > 0:
                    conditionalTree.generatePatterns(pattern)
            self.removeNode(i)


class Pufgrowth(frequentPatterns):
    """
        It is one of the fundamental algorithm to discover frequent patterns in a uncertain transactional database
        using PUF-Tree.

    Reference:
    --------
        Carson Kai-Sang Leung, Syed Khairuzzaman Tanbeer, "PUF-Tree: A Compact Tree Structure for Frequent Pattern Mining of Uncertain Data",
        Pacific-Asia Conference on Knowledge Discovery and Data Mining(PAKDD 2013), https://link.springer.com/chapter/10.1007/978-3-642-37453-1_2

    Attributes:
    ----------
        iFile : file
            Name of the Input file or path of the input file
        oFile : file
            Name of the output file or path of the output file
        minSup: float or int or str
            The user can specify minSup either in count or proportion of database size.
            If the program detects the data type of minSup is integer, then it treats minSup is expressed in count.
            Otherwise, it will be treated as float.
            Example: minSup=10 will be treated as integer, while minSup=10.0 will be treated as float
        sep : str
            This variable is used to distinguish items from one another in a transaction. The default seperator is tab space or \t.
            However, the users can override their default separator.
        memoryUSS : float
            To store the total amount of USS memory consumed by the program
        memoryRSS : float
            To store the total amount of RSS memory consumed by the program
        startTime:float
            To record the start time of the mining process
        endTime:float
            To record the completion time of the mining process
        Database : list
            To store the transactions of a database in list
        mapSupport : Dictionary
            To maintain the information of item and their frequency
        lno : int
            To represent the total no of transaction
        tree : class
            To represents the Tree class
        itemSetCount : int
            To represents the total no of patterns
        finalPatterns : dict
            To store the complete patterns
    Methods:
    -------
        startMine()
            Mining process will start from here
        getPatterns()
            Complete set of patterns will be retrieved with this function
        storePatternsInFile(oFile)
            Complete set of frequent patterns will be loaded in to a output file
        getPatternsInDataFrame()
            Complete set of frequent patterns will be loaded in to a dataframe
        getMemoryUSS()
            Total amount of USS memory consumed by the mining process will be retrieved from this function
        getMemoryRSS()
            Total amount of RSS memory consumed by the mining process will be retrieved from this function
        getRuntime()
            Total amount of runtime taken by the mining process will be retrieved from this function
        creatingItemSets(fileName)
            Scans the dataset and stores in a list format
        frequentOneItem()
            Extracts the one-length frequent patterns from database
        updateTransactions()
            Update the transactions by removing non-frequent items and sort the Database by item decreased support
        buildTree()
            After updating the Database, remaining items will be added into the tree by setting root node as null
        convert()
            to convert the user specified value
        startMine()
            Mining process will start from this function

    Executing the code on terminal:
    -------
        Format:
        ------
        python3 puf.py <inputFile> <outputFile> <minSup>
        Examples:
        --------
        python3 puf.py sampleTDB.txt patterns.txt 3    (minSup  will be considered in support count or frequency)

        
    Sample run of importing the code:
    -------------------

        from PAMI.uncertainFrequentPattern.basic import puf as alg

        obj = alg.Pufgrowth(iFile, minSup)

        obj.startMine()

        Patterns = obj.getPatterns()

        print("Total number of  Patterns:", len(Patterns))

        obj.storePatternsInFile(oFile)

        Df = obj.getPatternsInDataFrame()

        memUSS = obj.getMemoryUSS()

        print("Total Memory in USS:", memUSS)

        memRSS = obj.getMemoryRSS()

        print("Total Memory in RSS", memRSS)

        run = obj.getRuntime()

        print("Total ExecutionTime in seconds:", run)

    Credits:
    -------
        The complete program was written by P.Likhitha  under the supervision of Professor Rage Uday Kiran.\n

    """
    startTime = float()
    endTime = float()
    minSup = str()
    finalPatterns = {}
    iFile = " "
    oFile = " "
    sep = " "
    memoryUSS = float()
    memoryRSS = float()
    Database = []
    rank = {}

    def creatingItemSets(self):
        """
            Scans the dataset
        """
        try:
            with open(self.iFile, 'r') as f:
                for line in f:
                    l = [i.rstrip() for i in line.split(self.sep)]
                    tr = []
                    for i in l:
                        i1 = i.index('(')
                        i2 = i.index(')')
                        item = i[0:i1]
                        probability = float(i[i1 + 1:i2])
                        product = Item(item, probability)
                        tr.append(product)
                    self.Database.append(tr)
        except IOError:
            print("File Not Found")

    def frequentOneItem(self):
        """takes the self.Database and calculates the support of each item in the dataset and assign the
            ranks to the items by decreasing support and returns the frequent items list

                :param self.Database : it represents the one self.Database in database

                :type self.Database : list
        """

        mapSupport = {}
        for i in self.Database:
            for j in i:
                if j.item not in mapSupport:
                    mapSupport[j.item] = j.probability
                else:
                    mapSupport[j.item] += j.probability
        mapSupport = {k: v for k, v in mapSupport.items() if v >= self.minSup}
        plist = [k for k, v in sorted(mapSupport.items(), key=lambda x: x[1], reverse=True)]
        self.rank = dict([(index, item) for (item, index) in enumerate(plist)])
        return mapSupport, plist

    def buildTree(self, data, info):
        """it takes the self.Database and support of each item and construct the main tree with setting root
            node as null

                :param data : it represents the one self.Database in database

                :type data : list

                :param info : it represents the support of each item

                :type info : dictionary
        """

        rootNode = Tree()
        rootNode.info = info.copy()
        for i in range(len(data)):
            rootNode.addTransaction(data[i])
        return rootNode

    def updateTransactions(self, dict1):
        """remove the items which are not frequent from self.Database and updates the self.Database with rank of items


            :param dict1 : frequent items with support

            :type dict1 : dictionary
        """

        list1 = []
        for tr in self.Database:
            list2 = []
            for i in range(0, len(tr)):
                if tr[i].item in dict1:
                    list2.append(tr[i])
            if len(list2) >= 2:
                basket = list2
                basket.sort(key=lambda val: self.rank[val.item])
                list2 = basket
                list1.append(list2)
        return list1

    def check(self, i, x):
        """To check the presence of item or pattern in transaction

                :param x: it represents the pattern

                :type x : list

                :param i : represents the uncertain self.Database

                :type i : list
        """

        # This method taken a transaction as input and returns the tree
        for m in x:
            k = 0
            for n in i:
                if m == n.item:
                    k += 1
            if k == 0:
                return 0
        return 1

    def convert(self, value):
        """
        To convert the type of user specified minSup value

            :param value: user specified minSup value

            :return: converted type minSup value
        """
        if type(value) is int:
            value = int(value)
        if type(value) is float:
            value = float(value)
        if type(value) is str:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        return value
    
    def removeFalsePositives(self):
        """
            To remove the false positive patterns generated in frequent patterns

            :return: patterns with accurate probability
        """
        global finalPatterns
        periods = {}
        for i in self.Database:
            for x, y in finalPatterns.items():
                if len(x) == 1:
                    periods[x] = y
                else:
                    s = 1
                    check = self.check(i, x)
                    if check == 1:
                        for j in i:
                            if j.item in x:
                                s *= j.probability
                        if x in periods:
                            periods[x] += s
                        else:
                            periods[x] = s
        for x, y in periods.items():
            if y >= self.minSup:
                sample = str()
                for i in x:
                    sample = sample + i + " "
                self.finalPatterns[sample] = y

    def startMine(self):
        """Main method where the patterns are mined by constructing tree and remove the remove the false patterns
            by counting the original support of a patterns


        """
        global minSup
        self.startTime = time.time()
        self.creatingItemSets()
        self.minSup = self.convert(self.minSup)
        minSup = self.minSup
        mapSupport, plist = self.frequentOneItem()
        self.Database1 = self.updateTransactions(mapSupport)
        info = {k: v for k, v in mapSupport.items()}
        Tree1 = self.buildTree(self.Database1, info)
        Tree1.generatePatterns([])
        self.removeFalsePositives()
        print("Frequent patterns were generated from uncertain databases successfully using PUF algorithm")
        self.endTime = time.time()
        process = psutil.Process(os.getpid())
        self.memoryUSS = process.memory_full_info().uss
        self.memoryRSS = process.memory_info().rss

    def getMemoryUSS(self):
        """Total amount of USS memory consumed by the mining process will be retrieved from this function

        :return: returning USS memory consumed by the mining process

        :rtype: float
        """

        return self.memoryUSS

    def getMemoryRSS(self):
        """Total amount of RSS memory consumed by the mining process will be retrieved from this function

        :return: returning RSS memory consumed by the mining process

        :rtype: float
        """

        return self.memoryRSS

    def getRuntime(self):
        """Calculating the total amount of runtime taken by the mining process


        :return: returning total amount of runtime taken by the mining process

        :rtype: float
        """

        return self.endTime - self.startTime

    def getPatternsInDataFrame(self):
        """Storing final frequent patterns in a dataframe

        :return: returning frequent patterns in a dataframe

        :rtype: pd.DataFrame
        """

        dataframe = {}
        data = []
        for a, b in self.finalPatterns.items():
            data.append([a, b])
            dataframe = pd.DataFrame(data, columns=['Patterns', 'Support'])
        return dataframe

    def storePatternsInFile(self, outFile):
        """Complete set of frequent patterns will be loaded in to a output file

        :param outFile: name of the output file

        :type outFile: file
        """
        self.oFile = outFile
        writer = open(self.oFile, 'w+')
        for x, y in self.finalPatterns.items():
            s1 = x + ":" + str(y)
            writer.write("%s \n" % s1)

    def getPatterns(self):
        """ Function to send the set of frequent patterns after completion of the mining process

        :return: returning frequent patterns

        :rtype: dict
        """
        return self.finalPatterns


if __name__ == "__main__":
    ap = str()
    if len(sys.argv) == 4 or len(sys.argv) == 5:
        if len(sys.argv) == 5:
            ap = Pufgrowth(sys.argv[1], sys.argv[3], sys.argv[4])
        if len(sys.argv) == 4:
            ap = Pufgrowth(sys.argv[1], sys.argv[3])
        ap.startMine()
        Patterns = ap.getPatterns()
        print("Total number of Patterns:", len(Patterns))
        ap.storePatternsInFile(sys.argv[2])
        memUSS = ap.getMemoryUSS()
        print("Total Memory in USS:", memUSS)
        memRSS = ap.getMemoryRSS()
        print("Total Memory in RSS", memRSS)
        run = ap.getRuntime()
        print("Total ExecutionTime in ms:", run)
    else:
        print("Error! The number of input parameters do not match the total number of parameters provided")
