import numpy as np

def train_Elman(inputs, outputs, num_hidden, num_iters):
    """
    Initializes and trains an Elman network. For details see Elman (1990).

    Parameters
    ----------
    inputs : numpy array
        A one dimensional sequence of input values to the network

    outputs : numpy array
        A one-dimensional sequence of desired output values for each of the
        items in inputs

    num_hidden : int
        The number of hidden units to use in the network

    num_iters : int
        The number of training iterations to run the network for

    Returns
    -------
    net : dict
        Dictionary object containing the trained network weights for each layer. 
        Key 1 corresponds to the weights from the visibles to the hidden units,
        key 2 corresponds to the weights from the hiddens to the output units.

    NOTE: Poorly-Python-ported from trainElman.m, which in turn was adapted from
    code from http://www.cs.cmu.edu/afs/cs/academic/class/15782-f06/matlab/
    recurrent/ which in turn was adapted from Elman (1990) :-)
    """
    np.random.seed(seed=1)

    # Parameters
    # increment to the derivative of the transfer function (Fahlman's trick)
    DerivIncr = 0.2
    Momentum  = 0.05
    LearnRate = 0.001

    num_input  = 1
    num_output = 1
    num_train  = inputs.shape[0]

    if inputs.ndim == 2:
        num_input  = inputs.shape[0]
        num_output = outputs.shape[0]
        num_train  = inputs.shape[1]

    if not all([outputs.ndim == inputs.ndim,
               inputs.shape[0] == outputs.shape[0]]):
        raise ValueError('unequal number of input and output examples')

    # create a dictionary to hold the network weights
    net = {}
    net[1] = np.random.rand(num_hidden, num_input + num_hidden + 1) - 0.5
    net[2] = np.random.rand(num_output, num_hidden + 1) - 0.5

    # the context layer
    # zeros because it is not active when the network starts
    Result1 = np.zeros((num_hidden, num_train))

    # the row of ones is the bias
    Inputs = np.vstack((inputs, np.ones(num_train)))
    Desired = outputs

    delta_w1 = 0.
    delta_w2 = 0.

    # Training
    for ii in range(num_iters):
        # Recurrent state
        # includes current inputs, as well as the output of the hidden layer
        # from the previous time step
        Input1 = np.vstack((Inputs, np.hstack([np.zeros((num_hidden,1)),  Result1[:,:-1]])))

        # Forward propagate activations
        # input --> hidden
        NetIn1 = np.dot(net[1], Input1)
        Result1 = np.tanh(NetIn1)

        # Hidden --> output
        # we again add a row of ones for bias
        Input2 = np.vstack((Result1, np.ones(num_train)))
        NetIn2 = np.dot(net[2], Input2)
        Result2 = np.tanh(NetIn2)

        # Backprop errors
        # output --> hidden
        Result2Error = Result2 - Desired
        In2Error = Result2Error * (DerivIncr + np.cosh(NetIn2)**(-2))

        # hidden --> input
        Result1Error = np.dot(net[2].T, In2Error)
        In1Error = Result1Error[:-1, :] * (DerivIncr + np.cosh(NetIn1)**(-2))

        # Calculate weight updates
        dw2 = np.dot(In2Error, Input2.T)
        dw1 = np.dot(In1Error, Input1.T)

        delta_w2 = -LearnRate * dw2 + Momentum * delta_w2
        delta_w1 = -LearnRate * dw1 + Momentum * delta_w1

        net[2] = net[2] + delta_w2
        net[1] = net[1] + delta_w1
    return net


def predict_Elman(net, inputs):
    """
    Uses the Elman network parameterized by the weights in net to generate
    predictions for the elements in inputs.

    Parameters
    ----------
    net : dict
        Dictionary object containing the trained network weights and
        recurrent connections as produced by train_Elman. Key 1 corresponds 
        to the weights from the visibles to the hidden units, key 2 
        corresponds to the weights from the hiddens to the output units.

    inputs : numpy array
        A one dimensional sequence of input values to the network

    Returns
    -------
    outputs : numpy array
        An array containing the predictions generated by the Elman network for the
        items in inputs.
        
    NOTE: Poorly-Python-ported from predictElman.m, which in turn was adapted from
    code from http://www.cs.cmu.edu/afs/cs/academic/class/15782-f06/matlab/
    recurrent/ which in turn was adapted from Elman (1990) :-)
    """
    num_output = 1
    num_hidden = net[1].shape[0]
    num_train  = inputs.shape[0]

    if inputs.ndim == 2:
        num_train = inputs.shape[1]

    Inputs = np.vstack((inputs, np.ones([1, num_train])))
    Result1 = np.zeros([num_hidden, 1])

    outputs = np.zeros(num_train)

    for i in range(num_train):
        Input1 = np.append(Inputs[:, i], Result1)
        NetIn1 = np.dot(net[1], Input1)
        Result1 = np.tanh(NetIn1)

        Input2 = np.append(Result1, np.ones((1, 1)))
        NetIn2 = np.dot(net[2], Input2)
        outputs[i] = np.tanh(NetIn2)
    return outputs
