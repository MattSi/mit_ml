import pdb
import numpy as np
import code_for_hw3_part2 as hw3

#-------------------------------------------------------------------------------
# Auto Data
#-------------------------------------------------------------------------------

# Returns a list of dictionaries.  Keys are the column names, including mpg.
auto_data_all = hw3.load_auto_data('auto-mpg.tsv')

# The choice of feature processing for each feature, mpg is always raw and
# does not need to be specified.  Other choices are hw3.standard and hw3.one_hot.
# 'name' is not numeric and would need a different encoding.
features = [('cylinders', hw3.raw),
            ('displacement', hw3.raw),
            ('horsepower', hw3.raw),
            ('weight', hw3.raw),
            ('acceleration', hw3.raw),
            ## Drop model_year by default
            ## ('model_year', hw3.raw),
            ('origin', hw3.raw)]

# Construct the standard data and label arrays
auto_data, auto_labels = hw3.auto_data_and_labels(auto_data_all, features)
print('auto data and labels shape', auto_data.shape, auto_labels.shape)

if False:                               # set to True to see histograms
    import matplotlib.pyplot as plt
    for feat in range(auto_data.shape[0]):
        print('Feature', feat, features[feat][0])
        # Plot histograms in one window, different colors
        plt.hist(auto_data[feat,auto_labels[0,:] > 0])
        plt.hist(auto_data[feat,auto_labels[0,:] < 0])
        plt.show()
        # Plot histograms in two windows, different colors
        fig,(a1,a2) = plt.subplots(nrows=2)
        a1.hist(auto_data[feat,auto_labels[0,:] > 0])
        a2.hist(auto_data[feat,auto_labels[0,:] < 0])
        plt.show()

#-------------------------------------------------------------------------------
# Analyze auto data
#-------------------------------------------------------------------------------
# Your code here to process the auto data
T_values = [1, 10, 50]
feature_sets = [
    [('cylinders', hw3.raw),('displacement', hw3.raw),('horsepower', hw3.raw),('weight', hw3.raw),('acceleration', hw3.raw),('origin', hw3.raw)],
    [('cylinders', hw3.one_hot),('displacement', hw3.standard),('horsepower', hw3.standard),('weight', hw3.standard),('acceleration', hw3.standard),('origin', hw3.one_hot)]
]
learners = {
    "perceptron": hw3.perceptron,
    "averaged_perceptron": hw3.averaged_perceptron
}

for learner_name, learner_fn in learners.items():
    for T in T_values:
        for i, features in enumerate(feature_sets, start=1):
            data, labels = hw3.auto_data_and_labels(auto_data_all, features)
            acc = hw3.xval_learning_alg(lambda d, l: learner_fn(d, l, {"T": T}), data, labels, 10)
            print(f"Accuracy ({learner_name}) for T= {T}, feature set {i} : {acc:.4f}")

print("=================================================================")


def get_feature_names(features):
    names = []
    for name, transform in features:
        if transform == hw3.raw or transform == hw3.standard:
            names.append(name)
        elif transform == hw3.one_hot:
            unique_vals = list(set(entry[name] for entry in auto_data_all))
            for val in unique_vals:
                names.append(f"{name}={val}")
    return names



best_features = [('cylinders', hw3.one_hot),('displacement', hw3.standard),('horsepower', hw3.standard),('weight', hw3.standard),('acceleration', hw3.standard),('origin', hw3.one_hot)]
data, labels = hw3.auto_data_and_labels(auto_data_all, best_features)
theta, theta_0 = hw3.averaged_perceptron(data, labels, {"T": 50})
impact = np.abs(theta).flatten()
max_index = np.argmax(impact)
feature_names = get_feature_names(best_features)
print("影响最大的是：", feature_names[max_index])
print("=================================================================")

#-------------------------------------------------------------------------------
# Review Data
#-------------------------------------------------------------------------------

# Returns lists of dictionaries.  Keys are the column names, 'sentiment' and 'text'.
# The train data has 10,000 examples
review_data = hw3.load_review_data('reviews.tsv')

# Lists texts of reviews and list of labels (1 or -1)
review_texts, review_label_list = zip(*((sample['text'], sample['sentiment']) for sample in review_data))

# The dictionary of all the words for "bag of words"
dictionary = hw3.bag_of_words(review_texts)

# The standard data arrays for the bag of words
review_bow_data = hw3.extract_bow_feature_vectors(review_texts, dictionary)
review_labels = hw3.rv(review_label_list)
print('review_bow_data and labels shape', review_bow_data.shape, review_labels.shape)

#-------------------------------------------------------------------------------
# Analyze review data
#-------------------------------------------------------------------------------

# Your code here to process the review data

T_Values = [1, 10, 50]
learners = {
    "perceptron": hw3.perceptron,
    "averaged_perceptron": hw3.averaged_perceptron
}
print("Running 10-fold cross-validation on review data...\n")
theta, theta_0 = hw3.averaged_perceptron(review_bow_data, review_labels, {"T": 10})
reverse_dictionary = hw3.reverse_dict(dictionary)

# 找出权重最大的前10个索引
top_indices = np.argsort(theta.flatten())[::-1][:10]
bottom_indices = np.argsort(theta.flatten())[:10]

# 打印对应单词
top_words = [reverse_dictionary[i] for i in top_indices]
print("Top 10 most positive words:", top_words)

bottom_words = [reverse_dictionary[i] for i in bottom_indices]
print("Bottom 10 most negative words:", bottom_words)
#print(theta)
# for learner_name, learner_fn in learners.items():
#     for T in T_Values:
#         acc = hw3.xval_learning_alg(
#             lambda d, l: learner_fn(d, l, {"T": T}),
#             review_bow_data,
#             review_labels,
#             10
#         )
#         print(f"Accuracy ({learner_name}) for T = {T} : {acc:.4f}")

print("=================================================================")

#-------------------------------------------------------------------------------
# MNIST Data
#-------------------------------------------------------------------------------

"""
Returns a dictionary formatted as follows:
{
    0: {
        "images": [(m by n image), (m by n image), ...],
        "labels": [0, 0, ..., 0]
    },
    1: {...},
    ...
    9
}
Where labels range from 0 to 9 and (m, n) images are represented
by arrays of floats from 0 to 1
"""
mnist_data_all = hw3.load_mnist_data(range(10))

print('mnist_data_all loaded. shape of single images is', mnist_data_all[0]["images"][0].shape)

# HINT: change the [0] and [1] if you want to access different images
d0 = mnist_data_all[0]["images"]
d1 = mnist_data_all[1]["images"]
y0 = np.repeat(-1, len(d0)).reshape(1,-1)
y1 = np.repeat(1, len(d1)).reshape(1,-1)

# data goes into the feature computation functions
data = np.vstack((d0, d1))
# labels can directly go into the perceptron algorithm
labels = np.vstack((y0.T, y1.T)).T

def raw_mnist_features(x):
    """
    @param x (n_samples,m,n) array with values in (0,1)
    @return (m*n,n_samples) reshaped array where each entry is preserved
    """
    raise Exception("implement me!")

def row_average_features(x):
    """
    This should either use or modify your code from the tutor questions.

    @param x (n_samples,m,n) array with values in (0,1)
    @return (m,n_samples) array where each entry is the average of a row
    """
    raise Exception("modify me!")


def col_average_features(x):
    """
    This should either use or modify your code from the tutor questions.

    @param x (n_samples,m,n) array with values in (0,1)
    @return (n,n_samples) array where each entry is the average of a column
    """
    raise Exception("modify me!")


def top_bottom_features(x):
    """
    This should either use or modify your code from the tutor questions.

    @param x (n_samples,m,n) array with values in (0,1)
    @return (2,n_samples) array where the first entry of each column is the average of the
    top half of the image = rows 0 to floor(m/2) [exclusive]
    and the second entry is the average of the bottom half of the image
    = rows floor(m/2) [inclusive] to m
    """
    raise Exception("modify me!")

# use this function to evaluate accuracy
#acc = hw3.get_classification_accuracy(raw_mnist_features(data), labels)

#-------------------------------------------------------------------------------
# Analyze MNIST data
#-------------------------------------------------------------------------------

# Your code here to process the MNIST data

