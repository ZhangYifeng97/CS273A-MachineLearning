import numpy as np
import matplotlib.pyplot as plt
import mltools as ml
import cPickle as pickle
from sklearn.decomposition import PCA

X = np.genfromtxt("data/X_train.txt", delimiter = None)
Y = np.genfromtxt("data/Y_train.txt", delimiter = None)
# X, Y = ml.shuffleData(X,Y)
X, _ = ml.rescale(X)

components = range(1,15,1)
for component in components:
    print "="*50
    print "Number of Components = ", component
    pca = PCA(n_components=8)
    X_pca = pca.fit_transform(X)
    Xtr, Ytr = X_pca[:180000,:], Y[:180000]
    Xval, Yval = X_pca[180000:,:], Y[180000:]

    bags = [1,5,10,25,45,60,75]
    bagTrainError = []
    bagValidationError = []
    ensembles = []
    for bag in bags:
        print 'Training ', bag, ' decision tree(s)'
        decisionTrees = [None]*bag
        trainingError = []
        for i in range(0,bag,1):
            # Drawing a random training sample every single time
            Xi, Yi = ml.bootstrapData(Xtr,Ytr, n_boot=180000)
            decisionTrees[i] = ml.dtree.treeClassify(Xi, Yi, maxDepth=16, minLeaf=256)

        YHatValidation = np.zeros((Xval.shape[0], bag))
        YHatTraining = np.zeros((Xtr.shape[0], bag))
        for i in range(0,len(decisionTrees),1):
            decisionTree = decisionTrees[i]
            YHatValidation[:, i] = decisionTree.predict(Xval)
            YHatTraining[:,i] = decisionTree.predict(Xtr)

        # YHatValidation = np.sum(YHatValidation, axis=1)/float(bag)
        YHatValidation = np.mean(YHatValidation, axis=1)
        YHatValidation[YHatValidation > 0.5] = 1
        YHatValidation[YHatValidation <= 0.5] = 0

        # YHatTraining = np.sum(YHatTraining, axis=1)/float(bag)
        YHatTraining = np.mean(YHatTraining, axis=1)
        YHatTraining[YHatTraining > 0.5] = 1
        YHatTraining[YHatTraining <= 0.5] = 0

        bagValidationError.append(np.mean(YHatValidation != Yval))
        bagTrainError.append(np.mean(YHatTraining != Ytr))

        ensembles.append(decisionTrees)

    index = np.argmin(bagValidationError)
    print 'Minimum Validation Error = ', bagValidationError[index]
    print 'Number of learners in Bag = ', bags[index], " ", index

    with open("dtree_pca.mdl", "wb") as output_file:
        pickle.dump(ensembles, output_file)

# plt.plot(bags, bagTrainError, 'r', label='Training Error')
# plt.plot(bags, bagValidationError, 'g', label='Validation Error')
# plt.legend(loc='upper right')
# plt.title('Error vs # of Learners in Bag')
# plt.show()
