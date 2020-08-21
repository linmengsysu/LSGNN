# from layer import dilated_iso_layer
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from torch_geometric.nn import GCNConv, GATConv
# from torch_geometric.nn.conv import MessagePassing
# from torch_geometric.nn.inits import glorot, uniform
# from torch_geometric.utils import softmax

from layer import *
import pickle

class GNN(nn.Module):
    def __init__(self, n_layer, depth, dropout, in_dim, out_dim, num_types, device, bias=True):
        super(GNN, self).__init__()
        self.n_layer = n_layer
        self.depth = depth
        # print('in_dim=', in_dim)
        self.layer = GCNNet(out_dim, out_dim, n_layer, self.depth, dropout, device)
        self.f_linears   = nn.ModuleList()
        for t in range(num_types):
            self.f_linears.append(nn.Linear(in_dim, out_dim))

    def mp_linears(self, g):
        type_indices = g.node_type
        new_features = []
        for i in range(len(type_indices)):
            nf = self.f_linears[type_indices[i]](g.x[i])
            new_features.append(nf)
        g.x = torch.stack(new_features, dim=0)
        return g


    def mp(self, g):
        g = self.mp_linears(g)
        hs = self.layer(g)
        # print('message passing final embedding size={}'.format(hs.size()))
        return hs #torch.mean(hs, dim=1)

    def forward(self, g, types, features):
        return self.mp(g)

class Classifier(nn.Module):
    def __init__(self, n_hid, n_out):
        super(Classifier, self).__init__()
        self.n_hid    = n_hid
        self.n_out    = n_out
        self.linear   = nn.Linear(n_hid,  n_out)

    def forward(self, x):
        tx = self.linear(x)
        return torch.log_softmax(tx.squeeze(), dim=-1)

    def __repr__(self):
        return '{}(n_hid={}, n_out={})'.format(
            self.__class__.__name__, self.n_hid, self.n_out)




            
# class HeteroIsoNode(nn.Module):
#     def __init__(self, name, n_layer, depth, dropout, in_channels, out_channels, kernel_sizes, in_dim, out_dim, num_types, device, context_size=20, stride=1,
#                  padding=0, dilation=[1], groups=1,
#                  bias=True, padding_mode='zeros'):
#         super(HeteroIsoNode, self).__init__()
#         self.name = name
#         self.n_layer = n_layer
#         self.depth = depth
#         print('in_dim=', in_dim)
#         if name == 'isonode':
#             self.layers = [dilated_iso_layer(in_channels[i], out_channels[i], kernel_sizes[i], out_dim, out_dim, device, dilation=dilation[i]) for i in range(len(in_channels))]
#             for i, layer in enumerate(self.layers):
#                 self.add_module('layer_{}'.format(i), layer)
#             self.n_layer = len(self.layers)
#             self.ins = in_channels
#             self.outs = out_channels
        
#         elif name == 'mp':
#             self.layer = GCNNet(out_dim, out_dim, n_layer, self.depth, dropout, device)

#         self.f_linears   = nn.ModuleList()
#         self.c_linear = nn.Linear(num_types*context_size*out_dim, out_dim)
#         for t in range(num_types):
#             self.f_linears.append(nn.Linear(in_dim, out_dim))

#     def mp_linears(self, g):
#         type_indices = g.node_type
#         new_features = []
#         for i in range(len(type_indices)):
#             nf = self.f_linears[type_indices[i]](g.x[i])
#             new_features.append(nf)
#         g.x = torch.stack(new_features, dim=0)
#         return g

#     def flinears(self, features, node_types):
#         type_indices = node_types.detach()
#         new_features = []
#         for b in range(len(features)):
#             newf = []
#             for i in range(len(features[b])):
#                 # print('node_types[b][0][i]', int(node_types[b][0][i].item()))
#                 nf = self.f_linears[int(type_indices[b][0][i].item())](features[b][i])
#                 newf.append(nf)
#             newf = torch.stack(newf,dim=0)
#             new_features.append(newf)
#         new_features = torch.stack(new_features, dim=0)
#         # print('new_features', new_features.size())
#         return new_features

  
#     def isonode(self, g, types, features):
#         nfeatures = self.flinears(features, types)
#         hs = []
#         sim = []
#         for layer in self.layers:
#             h_l, sim_l = layer(g, types, nfeatures)
#             hs.append(h_l)
#             sim.append(sim_l) #[B, sub/64]
#         hs = torch.cat(hs, dim=-1) # [B, n_layer, out]
    
#         sim = torch.cat(sim, dim=-1)
#         pickle.dump(sim, open('./data/log_sim.pkl', 'wb'))
#         # print('only sim final embedding size={}'.format(sim.size()))
#         return hs #torch.mean(hs, dim=1)


#     def mp(self, g):
#         g = self.mp_linears(g)
#         hs = self.layer(g)
#         # print('message passing final embedding size={}'.format(hs.size()))
#         return hs #torch.mean(hs, dim=1)

#     def forward(self, g, types, features):
#         if self.name == 'isonode':
#             return self.isonode(g, types, features)
#         elif self.name == 'mp':
#             return self.mp(g)
