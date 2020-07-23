#  Machine Learning Parser

​	The tool was built for AI hardware/ software architectures to quickly understand and analyze the overall and layer-wise structure of neural network models. 

​	The types of results will be generated by the tool:

​	1) **tables** of parameters & statistics of network structure in excel format

​	2)  **graphs** of model structures in pdf format

## 1. Installation:

1.1. clone the repository to the local drive. 

1.2. The tool works with :

​		Python 3.6+, 

​		Tensorflow 2.1 +, 

​		Pytorch 1.5+

1.3. Install the following Python modules:

​		pandas
​		numpy
​		matplotlib
​		openpyxl
​		scikit-learn
​		scikit-image
​		graphviz
​		python-graphviz
​		pydot



## 2 Usages:

​	There are two versions of tools integrated in the package, one for ML framework pytorch: *torch2table*; the other is for Tensorflow via keras: *keras2table*.

#### 2.1. Pytorch version: torch2Table

##### 2.1.1. Command

- type the command as the following format to get the results

  ​	`python torch2table.py -n resnet50 -b 1 -e 1` 

- three optional arguments are:

  -n: the name of the neural network model. Tested models are listed below. Please note that the name is **case-sensitive**

  -b: batch-size of the input data

  -e: element size in byte, for example, float32 = 4, int8 =1, etc.

- The results are exported as the excel tables in ''/output/torch/''. 

##### 2.1.2. Tested models:

1. torchvision: 

   ​	alexnet, vgg11, vgg13, vgg16, vgg19, vgg11_bn, vgg_13 bn, vgg16_bn,

   ​	vgg19_bn, resnet18, resnet34, resnet50, resnet101, resnet152, 

   ​	SqueezeNet1_0, SqueezeNet1_1, densenet_121, densenet_169, densenet_201

   ​	densenet_161, inception_v3, googlenet, shufflenet_V2_x'n'_'n', mobileNet_v2

   ​	resnext_50_32x4d, resnext_101_32x8d, wide_resNet_50_2, wide_resnet_101_2

   ​	MNASNet'n'_'n'

2. Recomendation: dlrm

3. Others Models can also be imported, as long as a input tensor is provided  with the model. Please refer to **Section 4, example** **3** for details.

### 2.2. Tensorflow version: keras2table

##### 2.2.1. Command

- type the command as the following format to get the results

  ​	`python keras2table.py -n ResNet50 -b 1 -e 1` 

- three optional arguments are:

  -n: the name of the neural network model. Tested models are listed below. Please note that the name is **case-sensitive**

  -b: batch-size of the input data

  -e: element size in byte, for example, float32 = 4, int8 =1, etc.

- The results are exported as the excel tables in ''/output/tf/''

##### 2.2.2. Tested models:

1. keras pretrianed models: 

​    'DenseNet121', 'DenseNet169', 'DenseNet201',

​    'InceptionResNetV2', 'InceptionV3',

​     'MobileNet', 'MobileNetV2',

​     'NASNetLarge', 'NASNetMobile',

​     'ResNet101', 'ResNet101V2', 'ResNet152', 'ResNet152V2', 'ResNet50', 'ResNet50V2',

​     'VGG16', 'VGG19',

​     'Xception',

2. Reomendeation: din

3. EfficientNet: EfficientNetB0 ~ EfficientNetB7

4. NLP: bert

##### 2.2.3. Notes:

- keras-bert module should be installed for analysis,

    ​		`pip3 install keras-bert` 

- For DIN model, please clone the packages from [tensorflow/models](https://github.com/tensorflow/models) to a local folder, and add the folder into  PYTHONPATH



## 3. Outputs

​	There are two types of output files in the //outputs// torch// ( or //tf) folder: tables in xlsx and graph in pdf. Both are named as the input name of neural networks. 

### 3.1. The excel table with two sheets.  

#### 	3.1.1. summaries sheet:

​	 	Total counts of memory and computation costs. 

​			Note that  1M = 1024 x 1024, and 1G= 1M x 1024 in this table

#### 	3.1.2. Details sheet:

​		The results are demonstrated at one nn layer per row. The meanings of columns as belows:

​		**Layer:**

​			TF Keras: Layer names & Types

​			Pytorch:  layer names in multi-levels

​		**Input tensors :**

​			TF Keras version: 

​				I0_1,I0_2, I0_3: the shape of the first input

​				I1_1,I1_2,I1_3: the shape of the second input

​			Pytorch version:

​				I1, I2, I3: the shape of the first tensor

​		**Output tensors:** O1,O2,O3: th eshap of the first output

​		**Kernel Tensors:** 

​			k1,k2: kernel size H&W for conv & pooling; 

​			s1,s2: stride H&W of rolling windows;

​			p1,p2: padding size, values are calculated based on centric padding

​		**Memory Costs:** 

​			SizeI: Size of input tensors

​			SizeO: Size of output tensors

​			SizeW: Size of model parameters，note that the values depends on Byte per Elements(BPE) of the models, default BPE is 4 (fp32)

​		**Computation Costs:**

​			OpGemm: # of Matrix multi-adds

​			OpVect: # of Element-wise Ops

​			OpActi: # of activations(for transcendental Functions). Relu is also counted as an activation operation for convenience.

​		**misc:**

​			additional input/output tensors of the nn layer

​		**Color bars** of extreme cells

​			The cells/layers with the maximum  cost are marked as:

​				The maximum output Tensor:  Red,

​				The maximum weight tensor: Pink

​				The maximum matrix multi-add  costs : Green.

### 3.2  Model Graphs

​	A graph to visualize the model structure will be also generated with the same name as the table file.



## 4. Advances

​	One can further analyze the various configures of a NN models by changing default settings in the codes. Two examples are shown below.   

​	Note that the functions ( getmodel() & modelLst() ) mentioned below also demonstrate the ways to add a neural network model. Additional neural network models can be added using the similar approaches. 

### Example 1: bert in keras-tf

1. Bert models with different settings  

   These can be obtained by changing the optional arguments of  the 'get_model' function at line 312 in //utils//tftools//getmodel(), please refer to the [keras-bert](https://pypi.org/project/keras-bert/) for detailed settings for the bert model

2. inference model

   To get bert inference model, two revisions are required: 

   1. change training = Flase at line 310  //utils//tftools//getmodel()

   2. revise  `return inputs, transformed` -> `return inputs, transformed,model` at the orignal scirpts at line164 at \\\lib\\\site-packages\\\keras_bert\\\bert.py. Note that the operation will change the original codes of keras-bert

### Example 2:  dlrm in pytorch

1. Different settings of dlrm model

   The setting of dlrm model can be adjusted by changing values of variables at line44-47 in  in //utils//pytools//modellst(). Please refer to [DLRM](https://github.com/facebookresearch/dlrm) for the details of these variables.



### Example 3: Add a new model 

The  tool can parse a new model if one can add the model definition in the codes.  Steps to add a *pytorch* model  are shown below:

1. open the function modellst() in //utils//pytools.py

2. Assume the model name is "mymodel" as shown in line 78

3. Add the model definitions between line "===== To add a customized model ===="  and "===== end of your codes ======"

   A simple example for [pytorch tutoria](https://pytorch.org/tutorials/beginner/pytorch_with_examples.html)l is listed between these two lines. It can be easily replaced by other model definitions:

   - Define a random input tensor for the model    

     ​      `x = torch.randn(N, D_in)`

   - Get the model definition. 

     ​      `N, D_in, H, D_out = 64, 1000, 100, 10`

     ​      `model = torch.nn.Sequential(`

     ​      `torch.nn.Linear(D_in, H),`

     ​      `torch.nn.ReLU(),`

     ​      `torch.nn.Linear(H, D_out),`

     ​    `)`

     Instead of definition in the scripts, a predefined model can also be imported, 

      	 `model = predefinedModel(...)`

4. save the revised codes

5. in cmd window, type the command:

   ​	`python keras2table.py -n mymodel`

6. the corresponded graph and table will be exported into "//outputs//pytorch"

   

Steps to add a *keras* model are similar. Please refer to line 321-344 in GetModel() at [utils//tftools.py](./utils/tftools.py) for details.



Please note that special network structures and customized operators may not be supported by the tool. Feel free to join us to extend the functions of the tool.



### References:

- Codes for Pytorch model estimation were revised based on [torch-summary](https://github.com/TylerYep/torch-summary) @TylerYep
- Keras version EfficientNet is originated from [EfficientNet](https://github.com/qubvel/efficientnet/tree/master/efficientnet) @qubvel  
- DLRM is originated from [DLRM](https://github.com/facebookresearch/dlrm) by facebook