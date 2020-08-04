""" layer_info.py """
from typing import Any, Dict, List, Sequence, Union

import numpy as np
import torch
import torch.nn as nn

DETECTED_INPUT_TYPES = Union[Sequence[Any], Dict[Any, torch.Tensor], torch.Tensor] #0614
DETECTED_OUTPUT_TYPES = Union[Sequence[Any], Dict[Any, torch.Tensor], torch.Tensor]


class LayerInfo:
    """ Class that holds information about a layer module. """

    def __init__(self, module: nn.Module, depth: int, depth_index: int):
        # Identifying information
        self.layer_id = id(module)
        self.module = module
        self.class_name = str(module.__class__).split(".")[-1].split("'")[0]
        self.inner_layers = {}  # type: Dict[str, List[int]]
        self.depth = depth
        self.depth_index = depth_index

        # Statistics
        self.trainable = True
        self.is_recursive = False
        self.input_size = []    # 0614, func.copied from output_size
        self.output_size = []  # type: List[Union[int, Sequence[Any], torch.Size]]
        self.kernel_size = []  # type: List[int]
        self.stride_size = []   #0614,list: 1/2 elements
        self.pad_size = []  #0614
        self.num_params = 0
        self.macs = 0
        self.gemm = []
        self.vect = []
        self.acti = []

    def __repr__(self) -> str:
        return "{}: {}-{}".format(self.class_name, self.depth, self.depth_index)
    
    # 0614,
    def calculate_input_size(self, inputs: DETECTED_INPUT_TYPES, batch_dim: int) -> None:
        """ Set input_size using the model's inputs. """
        # if "LastLevelMaxPool" in self.class_name:
        #     print('multiple input List') #(tensor list,tensor list,list str)
        # if "MultiScaleRoIAlign" in self.class_name: #AnchorGenerator
        #     print('ImageList Gen')    
        if isinstance(inputs, (list, tuple)):
            try:
                self.input_size = list(inputs[0].size())
            except AttributeError:
                # pack_padded_seq and pad_packed_seq store feature into data attribute
                try:
                    size = list(inputs[0].data.size())
                except AttributeError:
                    if isinstance(inputs[0],list):
                        size = list(inputs[0][-2].shape)
                    else:
                        size = [1,0] #all other casse are blank
                        # print(self.class_name)
                self.input_size = size[:batch_dim] + [-1] + size[batch_dim + 1 :]

        elif isinstance(inputs, dict):
            for _, input in inputs.items():
                size = list(input.size())
                size_with_batch = size[:batch_dim] + [-1] + size[batch_dim + 1 :]
                self.input_size.append(size_with_batch)

        elif isinstance(inputs, torch.Tensor):
            self.input_size = list(inputs.size())
            self.input_size[batch_dim] = -1

        else:
            raise TypeError(
                "Model contains a layer with an unsupported input type: {}".format(inputs)
            )
            
    def calculate_output_size(self, outputs: DETECTED_OUTPUT_TYPES, batch_dim: int) -> None:
        """ Set output_size using the model's outputs. """
        # if "LastLevelMaxPool" in self.class_name: 
        #     print('multiple output Lists') #(tensor list,list str)
        # if "GeneralizedRCNNTransform" in self.class_name:
        #     print('ImageList Gen')
        if isinstance(outputs, (list, tuple)):
            try:
                self.output_size = list(outputs[0].size())
            except AttributeError:
                  # pack_padded_seq and pad_packed_seq store feature into data attribute
                try:
                    size = list(outputs[0].data.size())
                except AttributeError:
                    if isinstance(outputs[0],list):                        
                        if isinstance(outputs[0][-1],torch.Tensor):
                            size = list(outputs[0][-1].shape)
                        elif isinstance(outputs[0][-1],dict): # detection results in rcnn
                            size = [1, len(outputs[0][-1])]
                        else:
                            size = [1,0] #other cases for output[0][0]
                            print(self.class_name)
                    else:
                        size = [1,0] #all other casse are blank
                self.output_size = size[:batch_dim] + [-1] + size[batch_dim + 1 :]

        elif isinstance(outputs, dict):
            for _, output in outputs.items():
                size = list(output.size())
                size_with_batch = size[:batch_dim] + [-1] + size[batch_dim + 1 :]
                self.output_size.append(size_with_batch)

        elif isinstance(outputs, torch.Tensor):
            self.output_size = list(outputs.size())
            self.output_size[batch_dim] = -1

        else:
            raise TypeError(
                "Model contains a layer with an unsupported output type: {}".format(outputs)
            )

    def calculate_num_params(self) -> None:
        ub=0 # bias flag
        if hasattr(self.module,'stride'):  #0614
            if isinstance(self.module.stride,tuple):
                self.stride_size = list(self.module.stride)
            else: # make a 2 elem list for unified output
                self.stride_size = [self.module.stride,'']
            
        if hasattr(self.module,'padding'): #0614
            if isinstance(self.module.padding,tuple):
                self.pad_size = list(self.module.padding)
            else: # make a 2 elem list
                self.pad_size = [self.module.padding,'']
            
        """ Set num_params using the module's parameters.  """
        for name, param in self.module.named_parameters():
            self.num_params += param.nelement()
            self.trainable &= param.requires_grad
            # ignore N, C when calculate Mult-Adds in ConvNd
                                
            if name == "weight":
                ksize = list(param.size())
                # to make [in_shape, out_shape, ksize, ksize]
                if len(ksize) > 1:
                    ksize[0], ksize[1] = ksize[1], ksize[0]
                self.kernel_size = ksize

                # ignore N, C when calculate Mult-Adds in ConvNd
                if "Conv" in self.class_name:
                    self.macs += (param.nelement() * int(np.prod(self.output_size[2:])))
                else:
                    self.macs += param.nelement()
            # RNN modules have inner weights such as weight_ih_l0
            elif "weight" in name:
                self.inner_layers[name] = list(param.size())
                self.macs += param.nelement()
            
            if name == "bias":
                ub=1
                
        if "Conv" in self.class_name:
            units= int(np.prod(self.output_size[1:]))
            self.gemm = int(np.prod(self.output_size[2:])) *int(np.prod(self.kernel_size))+units*ub
        elif "BatchNorm2d" in self.class_name:
            self.vect = int(np.prod(self.output_size[1:]))*2 #1 elem* 1elem+
        elif "ReLU" in self.class_name:
            self.acti = int(np.prod(self.output_size[1:])）
        elif "MaxPool2d" in self.class_name:
            ksize=self.module.kernel_size
            csize=self.output_size[1]
            self.kernel_size=(csize,csize,ksize,ksize)
            self.vect = int(np.prod(self.output_size[1:]))*int(np.prod(self.kernel_size[2:])-1)            
        elif "Linear" in self.class_name:
            # lens = self.input_size[1]
            # units= self.output_size[1]
            #self.gemm = lens*units+ units*ub
            self.gemm = self.macs
        elif "Sigmoid" in self.class_name:
            self.acti = self.output_size[1]
        else:
            self.gemm = self.macs
        
        for name,aa in self.module.named_children(): 
            self.num_params = 0
            self.input_size = [0]*4
            self.output_size = [0]*4
            #print(self.class_name)
            break
           
    def check_recursive(self, summary_list: "List[LayerInfo]") -> None:
        """ if the current module is already-used, mark as (recursive).
        Must check before adding line to the summary. """
        if list(self.module.named_parameters()):
            for other_layer in summary_list:
                if self.layer_id == other_layer.layer_id:
                    self.is_recursive = True

    def macs_to_str(self, reached_max_depth: bool) -> str:
        """ Convert MACs to string. """
        if self.num_params > 0 and (reached_max_depth or not any(self.module.children())):
            return "{:,}".format(self.macs)
        return "--"

    def num_params_to_str(self, reached_max_depth: bool = False) -> str:
        """ Convert num_params to string. """
        assert self.num_params >= 0
        if self.is_recursive:
            return "(recursive)"
        if self.num_params > 0:
            param_count_str = "{:,}".format((self.num_params))
            if reached_max_depth or not any(self.module.children()):
                if not self.trainable:
                    return "({})".format(param_count_str)
                return param_count_str
        return "--"