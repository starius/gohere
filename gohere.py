#!/usr/bin/env python3

""" Install Go into a local directory. """

import argparse
import errno
import hashlib
import io
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import textwrap
try:
    import urllib2
except:
    # Python 3
    import urllib.request as urllib2


VERSIONS = {
    '1.4-bootstrap-20171003': 'f4ff5b5eb3a3cae1c993723f3eab519c5bae18866b5e5f96fe1102f0cb5c3e52',
    '1.5': 'be81abec996d5126c05f2d36facc8e58a94d9183a56f026fc9441401d80062db',
    '1.5.1': 'a889873e98d9a72ae396a9b7dd597c29dcd709cafa9097d9c4ba04cff0ec436b',
    '1.5.2': 'f3ddd624c00461641ce3d3a8d8e3c622392384ca7699e901b370a4eac5987a74',
    '1.5.3': '754e06dab1c31ab168fc9db9e32596734015ea9e24bc44cae7f237f417ce4efe',
    '1.5.4': '002acabce7ddc140d0d55891f9d4fcfbdd806b9332fb8b110c91bc91afb0bc93',
    '1.6': 'a96cce8ce43a9bf9b2a4c7d470bc7ee0cb00410da815980681c8353218dcf146',
    '1.6.1': '1d4b53cdee51b2298afcf50926a7fa44b286f0bf24ff8323ce690a66daa7193f',
    '1.6.2': '787b0b750d037016a30c6ed05a8a70a91b2e9db4bd9b1a2453aa502a63f1bccc',
    '1.6.3': '6326aeed5f86cf18f16d6dc831405614f855e2d416a91fd3fdc334f772345b00',
    '1.6.4': '8796cc48217b59595832aa9de6db45f58706dae68c9c7fbbd78c9fdbe3cd9032',
    '1.7': '72680c16ba0891fcf2ccf46d0f809e4ecf47bbf889f5d884ccb54c5e9a17e1c0',
    '1.7.1': '2b843f133b81b7995f26d0cb64bbdbb9d0704b90c44df45f844d28881ad442d3',
    '1.7.3': '79430a0027a09b0b3ad57e214c4c1acfdd7af290961dd08d322818895af1ef44',
    '1.7.4': '4c189111e9ba651a2bb3ee868aa881fab36b2f2da3409e80885ca758a6b614cc',
    '1.7.5': '4e834513a2079f8cbbd357502cccaac9507fd00a1efe672375798858ff291815',
    '1.7.6': '1a67a4e688673fdff7ba41e73482b0e59ac5bd0f7acf703bc6d50cc775c5baba',
    '1.8': '406865f587b44be7092f206d73fc1de252600b79b3cacc587b74b5ef5c623596',
    '1.8.1': '33daf4c03f86120fdfdc66bddf6bfff4661c7ca11c5da473e537f4d69b470e57',
    '1.8.2': 'e10401faaa8ae29dbe87349c1814b07b1903d453f822215d7b274bbc335cbf79',
    '1.8.3': '5f5dea2447e7dcfdc50fa6b94c512e58bfba5673c039259fd843f68829d99fa6',
    '1.8.4': 'abf1b2e5ae2a4845f3d2eac00c7382ff209e2c132dc35b7ce753da9b4f52e59f',
    '1.8.5': '4949fd1a5a4954eb54dd208f2f412e720e23f32c91203116bed0387cf5d0ff2d',
    '1.8.6': 'efc1221d3ae033c69e149801eff1d9872e214832a89f089fc5beb7a9fd98d9fb',
    '1.8.7': '5911e751807eebbc1980dad4305ef5492b96d6cd720bf93cbcefa86e1c195f9e',
    '1.9': 'a4ab229028ed167ba1986825751463605264e44868362ca8e7accc8be057e993',
    '1.9.1': 'a84afc9dc7d64fe0fa84d4d735e2ece23831a22117b50dafc75c1484f1cb550e',
    '1.9.2': '665f184bf8ac89986cfd5a4460736976f60b57df6b320ad71ad4cef53bb143dc',
    '1.9.3': '4e3d0ad6e91e02efa77d54e86c8b9e34fbe1cbc2935b6d38784dca93331c47ae',
    '1.9.4': '0573a8df33168977185aa44173305e5a0450f55213600e94541604b75d46dc06',
    '1.9.5': 'f1c2bb7f32bbd8fa7a19cc1608e0d06582df32ff5f0340967d83fb0017c49fbc',
    '1.9.6': '36f4059be658f7f07091e27fe04bb9e97a0c4836eb446e4c5bac3c90ff9e5828',
    '1.9.7': '582814fa45e8ecb0859a208e517b48aa0ad951e3b36c7fff203d834e0ef27722',
    '1.10': 'f3de49289405fda5fd1483a8fe6bd2fa5469e005fd567df64485c4fa000c7f24',
    '1.10.1': '589449ff6c3ccbff1d391d4e7ab5bb5d5643a5a41a04c99315e55c16bbf73ddc',
    '1.10.2': '6264609c6b9cd8ed8e02ca84605d727ce1898d74efa79841660b2e3e985a98bd',
    '1.10.3': '567b1cc66c9704d1c019c50bef946272e911ec6baf244310f87f4e678be155f2',
    '1.10.4': '6fe44965ed453cd968a81988523e9b0e794d3a478f91fd7983c28763d52d5781',
    '1.10.5': 'f0a3ed5c775f39a970d4937c64b3b178992e23a5df57ae56a59a1c99253094f4',
    '1.10.6': '0f6bd961f6d2d6fa6319b7dc9548e2ae22d0698e7432d4cabf737542913f8c14',
    '1.10.7': 'b84a0d7c90789f3a2ec5349dbe7419efb81f1fac9289b6f60df86bd919bd4447',
    '1.10.8': '6faf74046b5e24c2c0b46e78571cca4d65e1b89819da1089e53ea57539c63491',
    '1.11': 'afc1e12f5fe49a471e3aae7d906c73e9d5b1fdd36d52d72652dde8f6250152fb',
    '1.11.1': '558f8c169ae215e25b81421596e8de7572bd3ba824b79add22fba6e284db1117',
    '1.11.2': '042fba357210816160341f1002440550e952eb12678f7c9e7e9d389437942550',
    '1.11.3': '7ec5140f384db2bd42b396c93c231dfba342ee137ad8a4b33120016951eb1231',
    '1.11.4': '4cfd42720a6b1e79a8024895fa6607b69972e8e32446df76d6ce79801bbadb15',
    '1.11.5': 'bc1ef02bb1668835db1390a2e478dcbccb5dd16911691af9d75184bbe5aa943e',
    '1.11.6': 'a96da1425dcbec094736033a8a416316547f8100ab4b72c31d4824d761d3e133',
    '1.11.7': 'cfbe1078fbb1e34e77ad09de40d96d47ef280ba15791da9f02fc05486a4b16bd',
    '1.11.8': 'ba18bf8daf89218f9f2d853b3a9bc117d0ac24d3c98dac3474ed9ff9bf8efead',
    '1.11.9': 'ee80684b352f8d6b49d804d4e615f015ae92da41c4096cfee89ed4783b2498e3',
    '1.11.10': 'df27e96a9d1d362c46ecd975f1faa56b8c300f5c529074e9ea79bdd885493c1b',
    '1.11.11': '1fff7c33ef2522e6dfaf6ab96ec4c2a8b76d018aae6fc88ce2bd40f2202d0f8c',
    '1.11.12': '6d7a5ba05476609a7614af3292f29c3be06327503c1f1fdc02ef417870fd6926',
    '1.11.13': '5032095fd3f641cafcce164f551e5ae873785ce7b07ca7c143aecd18f7ba4076',
    '1.12': '09c43d3336743866f2985f566db0520b36f4992aea2b4b2fd9f52f17049e88f2',
    '1.12.1': '0be127684df4b842a64e58093154f9d15422f1405f1fcff4b2c36ffc6a15818a',
    '1.12.2': 'af992580a4a609309c734d46fd4374fe3095961263e609d9b017e2dffc3b7b58',
    '1.12.3': '5c507abe8818429d74ebb650a4155d36bc3f9a725e59e76f5d6aca9690be2373',
    '1.12.4': '4affc3e610cd8182c47abbc5b0c0e4e3c6a2b945b55aaa2ba952964ad9df1467',
    '1.12.5': '2aa5f088cbb332e73fc3def546800616b38d3bfe6b8713b8a6404060f22503e8',
    '1.12.6': 'c96c5ccc7455638ae1a8b7498a030fe653731c8391c5f8e79590bce72f92b4ca',
    '1.12.7': '95e8447d6f04b8d6a62de1726defbb20ab203208ee167ed15f83d7978ce43b13',
    '1.12.8': '11ad2e2e31ff63fcf8a2bdffbe9bfa2e1845653358daed593c8c2d03453c9898',
    '1.12.9': 'ab0e56ed9c4732a653ed22e232652709afbf573e710f56a07f7fdeca578d62fc',
    '1.12.10': 'f56e48fce80646d3c94dcf36d3e3f490f6d541a92070ad409b87b6bbb9da3954',
    '1.12.11': 'fcf58935236802929f5726e96cd1d900853b377bec2c51b2e37219c658a4950f',
    '1.12.12': 'fcb33b5290fa9bcc52be3211501540df7483d7276b031fc77528672a3c705b99',
    '1.12.13': '5383d3b8db4baa48284ffcb14606d9cad6f03e9db843fa6d835b94d63cccf5a7',
    '1.12.14': '39dbf05f7e2ffcb19b08f07d53dcc96feadeb1987fef9e279e7ff0c598213064',
    '1.12.15': '8aba74417e527524ad5724e6e6c21016795d1017692db76d1b0851c6bdec84c3',
    '1.12.16': 'ce6e5ed85b4a54ffc01d55a5838ee313acb4a7f109a745440fecbead1d081df8',
    '1.12.17': 'de878218c43aa3c3bad54c1c52d95e3b0e5d336e1285c647383e775541a28b25',
    '1.13': '3fc0b8b6101d42efd7da1da3029c0a13f22079c0c37ef9730209d8ec665bf122',
    '1.13.1': '81f154e69544b9fa92b1475ff5f11e64270260d46e7e36c34aafc8bc96209358',
    '1.13.2': '1ea68e01472e4276526902b8817abd65cf84ed921977266f0c11968d5e915f44',
    '1.13.3': '4f7123044375d5c404280737fbd2d0b17064b66182a65919ffe20ffe8620e3df',
    '1.13.4': '95dbeab442ee2746b9acf0934c8e2fc26414a0565c008631b04addb8c02e7624',
    '1.13.5': '27d356e2a0b30d9983b60a788cf225da5f914066b37a6b4f69d457ba55a626ff',
    '1.13.6': 'aae5be954bdc40bcf8006eb77e8d8a5dde412722bc8effcdaf9772620d06420c',
    '1.13.7': 'e4ad42cc5f5c19521fbbbde3680995f2546110b5c6aa2b48c3754ff7af9b41f4',
    '1.13.8': 'b13bf04633d4d8cf53226ebeaace8d4d2fd07ae6fa676d0844a688339debec34',
    '1.13.9': '34bb19d806e0bc4ad8f508ae24bade5e9fedfa53d09be63b488a9314d2d4f31d',
    '1.13.10': 'eb9ccc8bf59ed068e7eff73e154e4f5ee7eec0a47a610fb864e3332a2fdc8b8c',
    '1.13.11': '89ed1abce25ad003521c125d6583c93c1280de200ad221f961085200a6c00679',
    '1.13.12': '17ba2c4de4d78793a21cc659d9907f4356cd9c8de8b7d0899cdedcef712eba34',
    '1.13.13': 'ab7e44461e734ce1fd5f4f82c74c6d236e947194d868514d48a2b1ea73d25137',
    '1.13.14': '197333e97290e9ea8796f738d61019dcba1c377c2f3961fd6a114918ecc7ab06',
    '1.13.15': '5fb43171046cf8784325e67913d55f88a683435071eef8e9da1aa8a1588fcf5d',
    '1.14': '6d643e46ad565058c7a39dac01144172ef9bd476521f42148be59249e4b74389',
    '1.14.1': '2ad2572115b0d1b4cb4c138e6b3a31cee6294cb48af75ee86bec3dca04507676',
    '1.14.2': '98de84e69726a66da7b4e58eac41b99cbe274d7e8906eeb8a5b7eb0aadee7f7c',
    '1.14.3': '93023778d4d1797b7bc6a53e86c3a9b150c923953225f8a48a2d5fabc971af56',
    '1.14.4': '7011af3bbc2ac108d1b82ea8abb87b2e63f78844f0259be20cde4d42c5c40584',
    '1.14.5': 'ca4c080c90735e56152ac52cd77ae57fe573d1debb1a58e03da9cc362440315c',
    '1.14.6': '73fc9d781815d411928eccb92bf20d5b4264797be69410eac854babe44c94c09',
    '1.14.7': '064392433563660c73186991c0a315787688e7c38a561e26647686f89b6c30e3',
    '1.14.8': 'd9a613fb55f508cf84e753456a7c6a113c8265839d5b7fe060da335c93d6e36a',
    '1.14.9': 'c687c848cc09bcabf2b5e534c3fc4259abebbfc9014dd05a1a2dc6106f404554',
    '1.14.10': 'b37699a7e3eab0f90412b3969a90fd072023ecf61e0b86369da532810a95d665',
    '1.14.11': '1871f3d29b0cf1ebb739c9b134c9bc559282bd3625856e5f12f5aea29ab70f16',
    '1.14.12': 'b34f4b7ad799eab4c1a52bdef253602ce957125a512f5a1b28dce43c6841b971',
    '1.14.13': 'ba1d244c6b5c0ed04aa0d7856d06aceb89ed31b895de6ff783efb1cc8ab6b177',
    '1.14.14': '6204bf32f58fae0853f47f1bd0c51d9e0ac11f1ffb406bed07a0a8b016c8a76f',
    '1.14.15': '7ed13b2209e54a451835997f78035530b331c5b6943cdcd68a3d815fdc009149',
    '1.15': '69438f7ed4f532154ffaf878f3dfd83747e7a00b70b3556eddabf7aaee28ac3a',
    '1.15.1': 'd3743752a421881b5cc007c76b4b68becc3ad053e61275567edab1c99e154d30',
    '1.15.2': '28bf9d0bcde251011caae230a4a05d917b172ea203f2a62f2c2f9533589d4b4d',
    '1.15.3': '896a602570e54c8cdfc2c1348abd4ffd1016758d0bd086ccd9787dbfc9b64888',
    '1.15.4': '063da6a9a4186b8118a0e584532c8c94e65582e2cd951ed078bfd595d27d2367',
    '1.15.5': 'c1076b90cf94b73ebed62a81d802cd84d43d02dea8c07abdc922c57a071c84f1',
    '1.15.6': '890bba73c5e2b19ffb1180e385ea225059eb008eb91b694875dd86ea48675817',
    '1.15.7': '8631b3aafd8ecb9244ec2ffb8a2a8b4983cf4ad15572b9801f7c5b167c1a2abc',
    '1.15.8': '540c0ab7781084d124991321ed1458e479982de94454a98afab6acadf38497c2',
    '1.15.9': '90983b9c84a92417337dc1942ff066fc8b3a69733b8b5493fd0b9b9db1ead60f',
    '1.15.10': 'c1dbca6e0910b41d61a95bf9878f6d6e93d15d884c226b91d9d4b1113c10dd65',
    '1.15.11': 'f25b2441d4c76cf63cde94d59bab237cc33e8a2a139040d904c8630f46d061e5',
    '1.15.12': '1c6911937df4a277fa74e7b7efc3d08594498c4c4adc0b6c4ae3566137528091',
    '1.15.13': '99069e7223479cce4553f84f874b9345f6f4045f27cf5089489b546da619a244',
    '1.15.14': '60a4a5c48d63d0a13eca8849009b624629ff429c8bc5d1a6a8c3c4da9f34e70a',
    '1.15.15': '0662ae3813330280d5f1a97a2ee23bbdbe3a5a7cfa6001b24a9873a19a0dc7ec',
    '1.16': '7688063d55656105898f323d90a79a39c378d86fe89ae192eb3b7fc46347c95a',
    '1.16.1': '680a500cd8048750121677dd4dc055fdfd680ae83edc7ed60a4b927e466228eb',
    '1.16.2': '37ca14287a23cb8ba2ac3f5c3dd8adbc1f7a54b9701a57824bf19a0b271f83ea',
    '1.16.3': 'b298d29de9236ca47a023e382313bcc2d2eed31dfa706b60a04103ce83a71a25',
    '1.16.4': 'ae4f6b6e2a1677d31817984655a762074b5356da50fb58722b99104870d43503',
    '1.16.5': '7bfa7e5908c7cc9e75da5ddf3066d7cbcf3fd9fa51945851325eebc17f50ba80',
    '1.16.6': 'a3a5d4bc401b51db065e4f93b523347a4d343ae0c0b08a65c3423b05a138037d',
    '1.16.7': '1a9f2894d3d878729f7045072f30becebe243524cf2fce4e0a7b248b1e0654ac',
    '1.16.8': '8f2a8c24b793375b3243df82fdb0c8387486dcc8a892ca1c991aa99ace086b98',
    '1.16.9': '0a1cc7fd7bd20448f71ebed64d846138850d5099b18cf5cc10a4fc45160d8c3d',
    '1.16.10': 'a905472011585e403d00d2a41de7ced29b8884309d73482a307f689fd0f320b5',
    '1.16.11': '58041edcd81463b4cf1bc28b86dc0c17f4d9568d63c5afc85367dd8fae7befe7',
    '1.16.12': '2afd839dcb76d2bb082c502c01a0a5cdbfc09fd630757835363c4fde8e2fbfe8',
    '1.16.13': 'b0926654eaeb01ef43816638f42d7b1681f2d3f41b9559f07735522b7afad41a',
    '1.16.14': '467898cd3a216de54dcb9014f541efe77e9b79a7154dbc1fd2dd778b0c63fb56',
    '1.16.15': '90a08c689279e35f3865ba510998c33a63255c36089b3ec206c912fc0568c3d3',
    '1.17': '3a70e5055509f347c0fb831ca07a2bf3b531068f349b14a3c652e9b5b67beb5d',
    '1.17.1': '49dc08339770acd5613312db8c141eaf61779995577b89d93b541ef83067e5b1',
    '1.17.2': '2255eb3e4e824dd7d5fcdc2e7f84534371c186312e546fb1086a34c17752f431',
    '1.17.3': '705c64251e5b25d5d55ede1039c6aa22bea40a7a931d14c370339853643c3df0',
    '1.17.4': '4bef3699381ef09e075628504187416565d710660fec65b057edf1ceb187fc4b',
    '1.17.5': '3defb9a09bed042403195e872dcbc8c6fae1485963332279668ec52e80a95a2d',
    '1.17.6': '4dc1bbf3ff61f0c1ff2b19355e6d88151a70126268a47c761477686ef94748c8',
    '1.17.7': 'c108cd33b73b1911a02b697741df3dea43e01a5c4e08e409e8b3a0e3745d2b4d',
    '1.17.8': '2effcd898140da79a061f3784ca4f8d8b13d811fb2abe9dad2404442dabbdf7a',
    '1.17.9': '763ad4bafb80a9204458c5fa2b8e7327fa971aee454252c0e362c11236156813',
    '1.17.10': '299e55af30f15691b015d8dcf8ecae72412412569e5b2ece20361753a456f2f9',
    '1.17.11': 'ac2649a65944c6a5abe55054000eee3d77196880da36a3555f62e06540e8eb54',
    '1.17.12': '0d51b5b3f280c0f01f534598c0219db5878f337da6137a9ee698777413607209',
    '1.17.13': 'a1a48b23afb206f95e7bbaa9b898d965f90826f6f1d1fc0c1d784ada0cd300fd',
    '1.18': '38f423db4cc834883f2b52344282fa7a39fbb93650dc62a11fdf0be6409bdad6',
    '1.18.1': 'efd43e0f1402e083b73a03d444b7b6576bb4c539ac46208b63a916b69aca4088',
    '1.18.2': '2c44d03ea2c34092137ab919ba602f2c261a038d08eb468528a3f3a28e5667e2',
    '1.18.3': '0012386ddcbb5f3350e407c679923811dbd283fcdc421724931614a842ecbc2d',
    '1.18.4': '4525aa6b0e3cecb57845f4060a7075aafc9ab752bb7b6b4cf8a212d43078e1e4',
    '1.18.5': '9920d3306a1ac536cdd2c796d6cb3c54bc559c226fc3cc39c32f1e0bd7f50d2a',
    '1.18.6': 'a7f1d50424355dabce66d1112b1cae439b6ee5e4f15edba6f104c0a4b173e895',
    '1.18.7': '9467e33b819f71bebb21fb0ee1dd6794fd2244ae94907a984286712f9839a944',
    '1.18.8': '1f79802305015479e77d8c641530bc54ec994657d5c5271e0172eb7118346a12',
    '1.18.9': 'fbe7f09b96aca3db6faeaf180da8bb632868ec049731e355ff61695197c0e3ea',
    '1.18.10': '9cedcca58845df0c9474ae00274c44a95c9dfaefb132fc59921c28c7c106f8e6',
    '1.19': '9419cc70dc5a2523f29a77053cafff658ed21ef3561d9b6b020280ebceab28b9',
    '1.19.1': '27871baa490f3401414ad793fba49086f6c855b1c584385ed7771e1204c7e179',
    '1.19.2': '2ce930d70a931de660fdaf271d70192793b1b240272645bf0275779f6704df6b',
    '1.19.3': '18ac263e39210bcf68d85f4370e97fb1734166995a1f63fb38b4f6e07d90d212',
    '1.19.4': 'eda74db4ac494800a3e66ee784e495bfbb9b8e535df924a8b01b1a8028b7f368',
    '1.19.5': '8e486e8e85a281fc5ce3f0bedc5b9d2dbf6276d7db0b25d3ec034f313da0375f',
    '1.19.6': 'd7f0013f82e6d7f862cc6cb5c8cdb48eef5f2e239b35baa97e2f1a7466043767',
    '1.19.7': '775bdf285ceaba940da8a2fe20122500efd7a0b65dbcee85247854a8d7402633',
    '1.19.8': '1d7a67929dccafeaf8a29e55985bc2b789e0499cb1a17100039f084e3238da2f',
    '1.19.9': '131190a4697a70c5b1d232df5d3f55a3f9ec0e78e40516196ffb3f09ae6a5744',
    '1.19.10': '13755bcce529747d5f2930dee034730c86d02bd3e521ab3e2bbede548d3b953f',
    '1.19.11': 'e25c9ab72d811142b7f41ff6da5165fec2d1be5feec3ef2c66bc0bdecb431489',
    '1.19.12': 'ee5d50e0a7fd74ba1b137cb879609aaaef9880bf72b5d1742100e38ae72bb557',
    '1.19.13': 'ccf36b53fb0024a017353c3ddb22c1f00bc7a8073c6aac79042da24ee34434d3',
    '1.20': '3a29ff0421beaf6329292b8a46311c9fbf06c800077ceddef5fb7f8d5b1ace33',
    '1.20.1': 'b5c1a3af52c385a6d1c76aed5361cf26459023980d0320de7658bae3915831a2',
    '1.20.2': '4d0e2850d197b4ddad3bdb0196300179d095bb3aefd4dfbc3b36702c3728f8ab',
    '1.20.3': 'e447b498cde50215c4f7619e5124b0fc4e25fb5d16ea47271c47f278e7aa763a',
    '1.20.4': '9f34ace128764b7a3a4b238b805856cc1b2184304df9e5690825b0710f4202d6',
    '1.20.5': '9a15c133ba2cfafe79652f4815b62e7cfc267f68df1b9454c6ab2a3ca8b96a88',
    '1.20.6': '62ee5bc6fb55b8bae8f705e0cb8df86d6453626b4ecf93279e2867092e0b7f70',
    '1.20.7': '2c5ee9c9ec1e733b0dbbc2bdfed3f62306e51d8172bf38f4f4e542b27520f597',
    '1.20.8': '38d71714fa5279f97240451956d8e47e3c1b6a5de7cb84137949d62b5dd3182e',
    '1.20.9': '4923920381cd71d68b527761afefa523ea18c5831b4795034c827e18b685cdcf',
    '1.20.10': '72d2f51805c47150066c103754c75fddb2c19d48c9219fa33d1e46696c841dbb',
    '1.20.11': 'd355c5ae3a8f7763c9ec9dc25153aae373958cbcb60dd09e91a8b56c7621b2fc',
    '1.20.12': 'c5bf934751d31c315c1d0bb5fb02296545fa6d08923566f7a5afec81f2ed27d6',
    '1.20.13': '0fe745c530f2f1d67193af3c5ea25246be077989ec5178df266e975f3532449e',
    '1.20.14': '1aef321a0e3e38b7e91d2d7eb64040666cabdcc77d383de3c9522d0d69b67f4e',
    '1.21.0': '818d46ede85682dd551ad378ef37a4d247006f12ec59b5b755601d2ce114369a',
    '1.21.1': 'bfa36bf75e9a1e9cbbdb9abcf9d1707e479bd3a07880a8ae3564caee5711cb99',
    '1.21.2': '45e59de173baec39481854490d665b726cec3e5b159f6b4172e5ec7780b2c201',
    '1.21.3': '186f2b6f8c8b704e696821b09ab2041a5c1ee13dcbc3156a13adcf75931ee488',
    '1.21.4': '47b26a83d2b65a3c1c1bcace273b69bee49a7a7b5168a7604ded3d26a37bd787',
    '1.21.5': '285cbbdf4b6e6e62ed58f370f3f6d8c30825d6e56c5853c66d3c23bcdb09db19',
    '1.21.6': '124926a62e45f78daabbaedb9c011d97633186a33c238ffc1e25320c02046248',
    '1.21.7': '00197ab20f33813832bff62fd93cca1c42a08cc689a32a6672ca49591959bff6',
    '1.21.8': 'dc806cf75a87e1414b5b4c3dcb9dd3e9cc98f4cfccec42b7af617d5a658a3c43',
    '1.21.9': '58f0c5ced45a0012bce2ff7a9df03e128abcc8818ebabe5027bb92bafe20e421',
    '1.21.10': '900e0afe8900c1ee65a8a8c4f0c5a3ca02dcf85c1d1cb13a652be22c21399394',
    '1.21.11': '42aee9bf2b6956c75a7ad6aa3f0a51b5821ffeac57f5a2e733a2d6eae1e6d9d2',
    '1.21.12': '30e68af27bc1f1df231e3ab74f3d17d3b8d52a089c79bcaab573b4f1b807ed4f',
    '1.21.13': '71fb31606a1de48d129d591e8717a63e0c5565ffba09a24ea9f899a13214c34d',
    '1.22.0': '4d196c3d41a0d6c1dfc64d04e3cc1f608b0c436bd87b7060ce3e23234e1f4d5c',
    '1.22.1': '79c9b91d7f109515a25fc3ecdaad125d67e6bdb54f6d4d98580f46799caea321',
    '1.22.2': '374ea82b289ec738e968267cac59c7d5ff180f9492250254784b2044e90df5a9',
    '1.22.3': '80648ef34f903193d72a59c0dff019f5f98ae0c9aa13ade0b0ecbff991a76f68',
    '1.22.4': 'fed720678e728a7ca30ba8d1ded1caafe27d16028fab0232b8ba8e22008fb784',
    '1.22.5': 'ac9c723f224969aee624bc34fd34c9e13f2a212d75c71c807de644bb46e112f6',
    '1.22.6': '9e48d99d519882579917d8189c17e98c373ce25abaebb98772e2927088992a51',
    '1.22.7': '66432d87d85e0cfac3edffe637d5930fc4ddf5793313fe11e4a0f333023c879f',
    '1.22.8': 'df12c23ebf19dea0f4bf46a22cbeda4a3eca6f474f318390ce774974278440b8',
    '1.22.9': 'e81a362f51aee2125722b018e46714e6a055a1954283414c0f937e737013db22',
    '1.22.10': '1e94fd48be750d1fafb4d9b3b6dd31a6e9d2735d339bf2462bc97b64ca4c1037',
    '1.22.11': 'a60c23dec95d10a2576265ce580f57869d5ac2471c4f4aca805addc9ea0fc9fe',
    '1.22.12': '012a7e1f37f362c0918c1dfa3334458ac2da1628c4b9cf4d9ca02db986e17d71',
    '1.23.0': '42b7a8e80d805daa03022ed3fde4321d4c3bf2c990a144165d01eeecd6f699c6',
    '1.23.1': '6ee44e298379d146a5e5aa6b1c5b5d5f5d0a3365eabdd70741e6e21340ec3b0d',
    '1.23.2': '36930162a93df417d90bd22c6e14daff4705baac2b02418edda671cdfa9cd07f',
    '1.23.3': '8d6a77332487557c6afa2421131b50f83db4ae3c579c3bc72e670ee1f6968599',
    '1.23.4': 'ad345ac421e90814293a9699cca19dd5238251c3f687980bbcae28495b263531',
    '1.23.5': 'a6f3f4bbd3e6bdd626f79b668f212fbb5649daf75084fb79b678a0ae4d97423b',
    '1.23.6': '039c5b04e65279daceee8a6f71e70bd05cf5b801782b6f77c6e19e2ed0511222',
    '1.24.0': 'd14120614acb29d12bcab72bd689f257eb4be9e0b6f88a8fb7e41ac65f8556e5',
}
BOOTSTRAP_VERSION = '1.4-bootstrap-20171003'
BOOTSTRAP_VERSION_1_17_13 = '1.17.13'
BOOTSTRAP_VERSION_1_20_14 = '1.20.14'
BOOTSTRAP_VERSION_1_22_12 = '1.22.12'
MIN_VERSION_BUILT_WITH_GO = '1.5'
MIN_VERSION_BUILT_WITH_GO_1_17_13 = '1.20'
MIN_VERSION_BUILT_WITH_GO_1_20_14 = '1.22'
MIN_VERSION_BUILT_WITH_GO_1_22_12 = '1.24'
RELOCATION_TYPE_42_VERSIONS = ('1.4.1', '1.4.2', '1.4.3')
MIN_VERSION_WITHOUT_INCLUDE = '1.5'
MIN_VERSION_GOENV_REQUIRED = '1.21.0'

# cmd/link: support new 386/amd64 relocations
# It is needed to fix build on Debian 8 Stretch.
# See https://github.com/golang/go/issues/13896
# Backport https://github.com/golang/go/commit/914db9f060b1fd3eb1f74d48f3b

RELOCATION_TYPE_42_PATCH = r'''
--- src/cmd/6l/asm.c
+++ src/cmd/6l/asm.c
@@ -117,6 +117,8 @@ adddynrel(LSym *s, Reloc *r)
 		}
 		return;
 	
+	case 256 + R_X86_64_REX_GOTPCRELX:
+	case 256 + R_X86_64_GOTPCRELX:
 	case 256 + R_X86_64_GOTPCREL:
 		if(targ->type != SDYNIMPORT) {
 			// have symbol
--- src/cmd/8l/asm.c
+++ src/cmd/8l/asm.c
@@ -115,6 +115,7 @@ adddynrel(LSym *s, Reloc *r)
 		return;		
 	
 	case 256 + R_386_GOT32:
+	case 256 + R_386_GOT32X:
 		if(targ->type != SDYNIMPORT) {
 			// have symbol
 			if(r->off >= 2 && s->p[r->off-2] == 0x8b) {
--- src/cmd/ld/elf.h
+++ src/cmd/ld/elf.h
@@ -502,8 +502,23 @@ typedef struct {
 #define	R_X86_64_DTPOFF32 21	/* Offset in TLS block */
 #define	R_X86_64_GOTTPOFF 22	/* PC relative offset to IE GOT entry */
 #define	R_X86_64_TPOFF32 23	/* Offset in static TLS block */
-
-#define	R_X86_64_COUNT	24	/* Count of defined relocation types. */
+#define R_X86_64_PC64           24
+#define R_X86_64_GOTOFF64       25
+#define R_X86_64_GOTPC32        26
+#define R_X86_64_GOT64          27
+#define R_X86_64_GOTPCREL64     28
+#define R_X86_64_GOTPC64        29
+#define R_X86_64_GOTPLT64       30
+#define R_X86_64_PLTOFF64       31
+#define R_X86_64_SIZE32         32
+#define R_X86_64_SIZE64         33
+#define R_X86_64_GOTPC32_TLSDEC 34
+#define R_X86_64_TLSDESC_CALL   35
+#define R_X86_64_TLSDESC        36
+#define R_X86_64_IRELATIVE      37
+#define R_X86_64_PC32_BND       40
+#define R_X86_64_GOTPCRELX      41
+#define R_X86_64_REX_GOTPCRELX  42
 
 
 #define	R_ALPHA_NONE		0	/* No reloc */
@@ -535,8 +550,6 @@ typedef struct {
 #define	R_ALPHA_JMP_SLOT	26	/* Create PLT entry */
 #define	R_ALPHA_RELATIVE	27	/* Adjust by program base */
 
-#define	R_ALPHA_COUNT		28
-
 
 #define	R_ARM_NONE		0	/* No relocation. */
 #define	R_ARM_PC24		1
@@ -578,8 +591,6 @@ typedef struct {
 #define	R_ARM_RPC24		254
 #define	R_ARM_RBASE		255
 
-#define	R_ARM_COUNT		38	/* Count of defined relocation types. */
-
 
 #define	R_386_NONE	0	/* No relocation. */
 #define	R_386_32	1	/* Add symbol value. */
@@ -612,8 +623,42 @@ typedef struct {
 #define	R_386_TLS_DTPMOD32 35	/* GOT entry containing TLS index */
 #define	R_386_TLS_DTPOFF32 36	/* GOT entry containing TLS offset */
 #define	R_386_TLS_TPOFF32 37	/* GOT entry of -ve static TLS offset */
-
-#define	R_386_COUNT	38	/* Count of defined relocation types. */
+#define R_386_NONE          0
+#define R_386_32            1
+#define R_386_PC32          2
+#define R_386_GOT32         3
+#define R_386_PLT32         4
+#define R_386_COPY          5
+#define R_386_GLOB_DAT      6
+#define R_386_JMP_SLOT      7
+#define R_386_RELATIVE      8
+#define R_386_GOTOFF        9
+#define R_386_GOTPC         10
+#define R_386_TLS_TPOFF     14
+#define R_386_TLS_IE        15
+#define R_386_TLS_GOTIE     16
+#define R_386_TLS_LE        17
+#define R_386_TLS_GD        18
+#define R_386_TLS_LDM       19
+#define R_386_TLS_GD_32     24
+#define R_386_TLS_GD_PUSH   25
+#define R_386_TLS_GD_CALL   26
+#define R_386_TLS_GD_POP    27
+#define R_386_TLS_LDM_32    28
+#define R_386_TLS_LDM_PUSH  29
+#define R_386_TLS_LDM_CALL  30
+#define R_386_TLS_LDM_POP   31
+#define R_386_TLS_LDO_32    32
+#define R_386_TLS_IE_32     33
+#define R_386_TLS_LE_32     34
+#define R_386_TLS_DTPMOD32  35
+#define R_386_TLS_DTPOFF32  36
+#define R_386_TLS_TPOFF32   37
+#define R_386_TLS_GOTDESC   39
+#define R_386_TLS_DESC_CALL 40
+#define R_386_TLS_DESC      41
+#define R_386_IRELATIVE     42
+#define R_386_GOT32X        43
 
 #define	R_PPC_NONE		0	/* No relocation. */
 #define	R_PPC_ADDR32		1
@@ -653,8 +698,6 @@ typedef struct {
 #define	R_PPC_SECTOFF_HI	35
 #define	R_PPC_SECTOFF_HA	36
 
-#define	R_PPC_COUNT		37	/* Count of defined relocation types. */
-
 #define R_PPC_TLS		67
 #define R_PPC_DTPMOD32		68
 #define R_PPC_TPREL16		69
@@ -697,9 +740,6 @@ typedef struct {
 #define	R_PPC_EMB_BIT_FLD	115
 #define	R_PPC_EMB_RELSDA	116
 
-					/* Count of defined relocation types. */
-#define	R_PPC_EMB_COUNT		(R_PPC_EMB_RELSDA - R_PPC_EMB_NADDR32 + 1)
-
 
 #define R_SPARC_NONE		0
 #define R_SPARC_8		1
--- src/cmd/ld/ldelf.c
+++ src/cmd/ld/ldelf.c
@@ -888,12 +888,15 @@ reltype(char *pn, int elftype, uchar *siz)
 	case R('6', R_X86_64_PC32):
 	case R('6', R_X86_64_PLT32):
 	case R('6', R_X86_64_GOTPCREL):
+	case R('6', R_X86_64_GOTPCRELX):
+	case R('6', R_X86_64_REX_GOTPCRELX):
 	case R('8', R_386_32):
 	case R('8', R_386_PC32):
 	case R('8', R_386_GOT32):
 	case R('8', R_386_PLT32):
 	case R('8', R_386_GOTOFF):
 	case R('8', R_386_GOTPC):
+	case R('8', R_386_GOT32X):
 		*siz = 4;
 		break;
 	case R('6', R_X86_64_64):
'''

# Code for patching was copied from hererocks.py commit 8afe7846572440de21e
# https://github.com/mpeterv/hererocks/
# Copyright (c) 2015 - 2016 Peter Melnichenko

class PatchError(Exception):
    pass

class LineScanner(object):
    def __init__(self, lines):
        self.lines = lines
        self.line_number = 1

    def consume_line(self):
        if self.line_number > len(self.lines):
            raise PatchError("source is too short")
        else:
            self.line_number += 1
            return self.lines[self.line_number - 2]

class Hunk(object):
    def __init__(self, start_line, lines):
        self.start_line = start_line
        self.lines = lines

    def add_new_lines(self, old_lines_scanner, new_lines):
        while old_lines_scanner.line_number < self.start_line:
            new_lines.append(old_lines_scanner.consume_line())

        for line in self.lines:
            first_char, rest = line[0], line[1:]

            if first_char in " -":
                # Deleting or copying a line: it must match what's in the diff.
                old_line = old_lines_scanner.consume_line()
                if rest.strip() != old_line.strip():
                    raise PatchError("source is different: %s, %s" % (
                        rest, old_line,
                    ))

            if first_char in " +":
                # Adding or copying a line: add it to the line list.
                new_lines.append(rest)

class FilePatch(object):
    def __init__(self, file_name, lines):
        self.file_name = file_name
        self.hunks = []
        self.new_lines = []
        hunk_lines = None
        start_line = None

        for line in lines:
            first_char = line[0]

            if first_char == "@":
                if start_line is not None:
                    self.hunks.append(Hunk(start_line, hunk_lines))

                match = re.match(r"^@@ \-(\d+)", line)
                start_line = int(match.group(1))
                hunk_lines = []
            else:
                hunk_lines.append(line)

        if start_line is not None:
            self.hunks.append(Hunk(start_line, hunk_lines))

    def prepare_application(self):
        if not os.path.exists(self.file_name):
            raise PatchError("{} doesn't exist".format(self.file_name))

        with open(self.file_name, "r") as handler:
            source = handler.read()

        old_lines = source.splitlines()
        old_lines_scanner = LineScanner(old_lines)

        for hunk in self.hunks:
            hunk.add_new_lines(old_lines_scanner, self.new_lines)

        while old_lines_scanner.line_number <= len(old_lines):
            self.new_lines.append(old_lines_scanner.consume_line())

        self.new_lines.append("")

    def apply(self):
        with open(self.file_name, "wt") as handler:
            handler.write("\n".join(self.new_lines))

class Patch(object):
    def __init__(self, src, root_dir):
        # The first and the last lines are empty.
        lines = textwrap.dedent(src[1:-1]).splitlines()
        lines = [line if line else " " for line in lines]
        self.file_patches = []
        file_lines = None
        file_name = None

        for line in lines:
            if line.startswith('--- '):
                continue
            if line.startswith('+++ '):
                if file_name is not None:
                    self.file_patches.append(FilePatch(file_name, file_lines))
                file_name = os.path.join(root_dir, line[4:])
                file_lines = []
            else:
                file_lines.append(line)

        if file_name is not None:
            self.file_patches.append(FilePatch(file_name, file_lines))

    def apply(self):
        try:
            for file_patch in self.file_patches:
                file_patch.prepare_application()
        except PatchError as e:
            return e.args[0]

        for file_patch in self.file_patches:
            file_patch.apply()

class TempDir(object):
    n = 0
    def __init__(self, echo=None, goroot=None):
        TempDir.n += 1
        self.echoname = 'T%d' % TempDir.n
        self.echodir = '%s/T%d' % (goroot, TempDir.n)
        self.echo = echo

    def __enter__(self):
        if self.echo:
            self.echo('%s="%s"' % (self.echoname, self.echodir))
            self.echo('mkdir -p "$%s"' % self.echoname)
            return '${%s}' % self.echoname
        else:
            self.name = tempfile.mkdtemp()
            return self.name

    def __exit__(self, type, value, traceback):
        if self.echo:
            self.echo('rm -rf "$%s"' % self.echoname)
        else:
            shutil.rmtree(self.name)

def version_tuple(version):
    if version == BOOTSTRAP_VERSION:
        version = "1.4.9"
    return tuple(map(int, (version.split('.'))))

def is_build_with_go(version):
    if version_tuple(version) >= version_tuple(MIN_VERSION_BUILT_WITH_GO_1_22_12):
        return BOOTSTRAP_VERSION_1_22_12
    if version_tuple(version) >= version_tuple(MIN_VERSION_BUILT_WITH_GO_1_20_14):
        return BOOTSTRAP_VERSION_1_20_14
    if version_tuple(version) >= version_tuple(MIN_VERSION_BUILT_WITH_GO_1_17_13):
        return BOOTSTRAP_VERSION_1_17_13
    if version_tuple(version) >= version_tuple(MIN_VERSION_BUILT_WITH_GO):
        return BOOTSTRAP_VERSION

def get_default_cache():
    # based on hererocks.py
    if os.name == 'nt':
        cache_root = os.getenv('LOCALAPPDATA')
        if cache_root is None:
            cache_root = os.getenv('USERPROFILE')
            if cache_root is None:
                return None
            cache_root = os.path.join(cache_root, 'Local Settings', 'Application Data')
        return os.path.join(cache_root, 'GoHere', 'Cache')
    else:
        home = os.path.expanduser('~')
        if home == '~':
            return None
        else:
            return os.path.join(home, '.cache', 'gohere')

def get_filename(version):
    if 'bootstrap' not in version:
        version += '.src'
    return 'go%s.tar.gz' % version

def get_url(version):
    return 'https://storage.googleapis.com/golang/%s' % get_filename(version)

def download_file(destination, url, echo=None):
    if echo:
        echo('wget -O "%s" "%s"' % (destination, url))
    else:
        with open(destination, 'wb') as d:
            request =  urllib2.urlopen(url)
            shutil.copyfileobj(request, d)
            request.close()
            logging.info('File %s was downloaded from %s', destination, url)

def checksum_of_file(fileobj):
    hasher = hashlib.sha256()
    for chunk in iter(lambda: fileobj.read(1024 ** 2), b''):
        hasher.update(chunk)
    return hasher.hexdigest()

def make_checksum(filepath):
    with open(filepath, 'rb') as f:
        value = checksum_of_file(f)
    logging.info('sha256(%s) = %s', filepath, value)
    return value

def test_checksum(filename, version, echo=None):
    expected_checksum = VERSIONS[version]
    if echo:
        echo('echo "%s  %s" | sha256sum --check --strict -' % (expected_checksum, filename))
    else:
        observed_checksum = make_checksum(filename)
        if expected_checksum == observed_checksum:
            logging.info('Checksum of %s is good', filename)
        else:
            logging.error(
                'Checksum of %s is bad.\nExpected %s,\nobserved %s.',
                filename,
                expected_checksum,
                observed_checksum,
            )
            sys.exit(1)

def is_within_directory(directory, target):
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)
    prefix = os.path.commonprefix([abs_directory, abs_target])
    return prefix == abs_directory

def unpack_file(parent_of_goroot, archive_name, echo=None):
    if echo:
        echo('tar -C "%s" -xzf "%s"' % (parent_of_goroot, archive_name))
    else:
        with tarfile.open(archive_name, 'r:gz') as archive:
            for member in archive.getmembers():
                member_path = os.path.join(parent_of_goroot, member.name)
                if not is_within_directory(parent_of_goroot, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
            archive.extractall(parent_of_goroot)
            logging.info('File %s was unpacked to %s', archive_name, parent_of_goroot)

def mkdir_p(path):
    # taken from http://stackoverflow.com/a/600612
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def patch_go(goroot, version, echo=None):
    if version_tuple(version) < version_tuple(MIN_VERSION_WITHOUT_INCLUDE):
        libc_h = os.path.join(goroot, 'include', 'libc.h')
        if echo:
            echo('sed -i.bak -e "s/struct timespec {/struct timespec_disabled_by_gohere {/g" -- "%s"' % libc_h)
        else:
            # https://ci.appveyor.com/project/starius/gohere/build/1.0.5/job/v08nsr6kj98s8xtu
            logging.info('Patching libc.h to fix conflicting timespec (WIN32)')
            with open(libc_h) as f:
                code = f.read()
            code = code.replace(
                'struct timespec {',
                'struct timespec_disabled_by_gohere {',
            )
            with open(libc_h, 'w') as f:
                f.write(code)
    # Fix "shifting a negative signed value is undefined" on clang.
    # See https://travis-ci.org/starius/gohere/jobs/169812907
    if echo:
        echo('find "%s" -name "*.c" -print0 | xargs -0 -I cfile sed -i.bak -e "s/(vlong)~0 << 32/(uvlong)~0 << 32/g" -- cfile' % goroot)
    else:
        for directory, _, files in os.walk(goroot):
            for base in files:
                if base.endswith('.c'):
                    path = os.path.join(directory, base)
                    with open(path) as f:
                        t = f.read()
                    if '(vlong)~0 << 32' in t:
                        logging.info('Patching %s to fix (vlong)~0 << 32', path)
                        t = t.replace('(vlong)~0 << 32', '(uvlong)~0 << 32')
                        with open(path, 'w') as f:
                            f.write(t)
    # Patch Go 1.4 to prevent https://github.com/golang/go/issues/13896
    # The patch is not applicable to Go 1.4 because line numbers shift.
    if version in RELOCATION_TYPE_42_VERSIONS:
        if echo:
            echo('cd "%s" && patch -p0 -u << EOF\n%s\nEOF' % (goroot, RELOCATION_TYPE_42_PATCH))
        else:
            logging.info('Patching to "fix unknown relocation type 42"')
            err = Patch(RELOCATION_TYPE_42_PATCH, goroot).apply()
            if err is not None:
                raise Exception(err)
    # Fix "implicit conversion from 'int' to 'char' changes" errors.
    # https://travis-ci.org/starius/gohere/jobs/323022483#L2346
    if version_tuple(version) < version_tuple(BOOTSTRAP_VERSION):
        dwarf_c = os.path.join(goroot, 'src', 'cmd', 'ld', 'dwarf.c')
        if echo:
            echo('sed -i.bak -e "s/DW_CFA_offset/((char)(DW_CFA_offset))/g" -- "%s"' % dwarf_c)
            echo('sed -i.bak -e "s/DW_OP_call_frame_cfa/((char)(DW_OP_call_frame_cfa))/g" -- "%s"' % dwarf_c)
        else:
            logging.info('Patching dwarf.c to fix implicit conversion errors')
            with open(dwarf_c) as f:
                code = f.read()
            code = code.replace('DW_CFA_offset', '((char)(DW_CFA_offset))')
            code = code.replace('DW_OP_call_frame_cfa', '((char)(DW_OP_call_frame_cfa))')
            with open(dwarf_c, 'w') as f:
                f.write(code)

def build_go(goroot_final, goroot, goroot_bootstrap=None, test=False, echo=None):
    action = 'all' if test else 'make'
    cwd = os.path.join(goroot, 'src')
    if not echo:
        cwd = os.path.abspath(cwd)
    if os.name == 'nt':
        # Otherwise Windows can not find the batch file
        args = [os.path.join(cwd, '%s.bat' % action)]
    else:
        args = ['./%s.bash' % action]
    if echo:
        echo(
            'cd "%s" && GOROOT_FINAL="%s" GOROOT_BOOTSTRAP="%s" %s | grep "Installed Go"' %
            (cwd, goroot_final, goroot_bootstrap or '', ' '.join(args))
        )
    else:
        env = os.environ.copy()
        env['GOROOT_FINAL'] = goroot_final
        if goroot_bootstrap:
            env['GOROOT_BOOTSTRAP'] = goroot_bootstrap
            logging.info('Go bootstrap is %s', goroot_bootstrap)
        logging.info('Building Go in %s', cwd)
        go_process = subprocess.Popen(
            args,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        (stdout_data, stderr_data) = go_process.communicate()
        logging.info('Exit code is %d', go_process.returncode)
        if not isinstance(stdout_data, str):
            stdout_data = stdout_data.decode()
        if not isinstance(stderr_data, str):
            stderr_data = stderr_data.decode()
        if go_process.returncode != 0 or 'Installed Go' not in stdout_data:
            logging.error('Failed to build Go.')
            logging.error('stdout: %s', stdout_data)
            logging.error('stderr: %s', stderr_data)
            sys.exit(1)
        logging.info('Go was built in %s', goroot)

def install_go(goroot_final, goroot, version, echo=None):
    if echo:
        echo('mkdir -p "%s"' % goroot_final)
    else:
        mkdir_p(goroot_final)
    dirs = ['src', 'bin', 'pkg', 'misc']
    if version_tuple(version) < version_tuple(MIN_VERSION_WITHOUT_INCLUDE):
        dirs.append('include')
    if echo:
        dirs2 = ['"%s"' % os.path.join(goroot, d) for d in dirs]
        echo('cp -a %s "%s"' % (' '.join(dirs2), goroot_final))
    else:
        for subdir in dirs:
            src = os.path.join(goroot, subdir)
            dst = os.path.join(goroot_final, subdir)
            shutil.copytree(src, dst)
    if version_tuple(version) >= version_tuple(MIN_VERSION_GOENV_REQUIRED):
        # Copy go.env file to fix "go: GOPROXY list is not the empty string, but contains no entries".
        # Disable dangerous settings.
        goenv_src = os.path.join(goroot, 'go.env')
        goenv_dst = os.path.join(goroot_final, 'go.env')
        if echo:
            echo('echo "Copying go.env file to %s"' % goroot_final)
            echo('cp %s %s' % (goenv_src, goenv_dst))
            echo('echo "Disabling dangerous settings in go.env"')
            echo('sed -i.bak -e "s/GOPROXY=.*/GOPROXY=direct/" -- "%s"' % goenv_dst)
            echo('sed -i.bak -e "s/GOSUMDB=.*/GOSUMDB=off/" -- "%s"' % goenv_dst)
            echo('sed -i.bak -e "s/GOTOOLCHAIN=.*/GOTOOLCHAIN=local/" -- "%s"' % goenv_dst)
        else:
            logging.info('Copying go.env file to %s', goroot_final)
            with io.open(goenv_src) as f:
                goenv_content = f.read()
            logging.info('Disabling dangerous settings in go.env')
            goenv_content = re.sub(r'GOPROXY=\S*', 'GOPROXY=direct', goenv_content)
            goenv_content = re.sub(r'GOSUMDB=\S*', 'GOSUMDB=off', goenv_content)
            goenv_content = re.sub(r'GOTOOLCHAIN=\S*', 'GOTOOLCHAIN=local', goenv_content)
            with io.open(goenv_dst, 'w', newline='\n') as f:
                f.write(goenv_content)
    if echo:
        echo('echo "Go was installed to %s"' % goroot_final)
    else:
        logging.info('Go was installed to %s', goroot_final)

def build_race(goroot, echo=None):
    # See https://github.com/golang/go/issues/20512
    go_binary = os.path.join(goroot, 'bin', 'go')
    args = [go_binary, 'install', '-v', '-race', 'std']
    if echo:
        echo(' '.join(args))
    else:
        logging.info('Building Go race in %s', goroot)
        go_process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        (stdout_data, stderr_data) = go_process.communicate()
        logging.info('Exit code is %d', go_process.returncode)
        if not isinstance(stdout_data, str):
            stdout_data = stdout_data.decode()
        if not isinstance(stderr_data, str):
            stderr_data = stderr_data.decode()
        if go_process.returncode != 0:
            logging.error('Failed to build Go.')
            logging.error('stdout: %s', stdout_data)
            logging.error('stderr: %s', stderr_data)
            sys.exit(1)

def get_from_cache_or_download(cache_root, version, tmp_dir, echo=None):
    filename = get_filename(version)
    if not echo and cache_root:
        file_in_cache = os.path.join(cache_root, filename)
        if os.path.isfile(file_in_cache):
            test_checksum(file_in_cache, version)
            logging.info('Reusing file from cache: %s', file_in_cache)
            return file_in_cache
    tmp_name = os.path.join(tmp_dir, filename)
    download_file(tmp_name, get_url(version), echo)
    test_checksum(tmp_name, version, echo)
    if not echo and cache_root:
        mkdir_p(cache_root)
        shutil.move(tmp_name, file_in_cache)
        logging.info('New file was added to cache: %s', file_in_cache)
        return file_in_cache
    else:
        return tmp_name

def make_goroot_bootstrap(cache_root, tmp_dir, echo=None, bootstrap_version=BOOTSTRAP_VERSION):
    subdir = 'go%s_bootstrap' % bootstrap_version
    if not echo and cache_root:
        goroot_bootstrap = os.path.join(cache_root, subdir)
        if os.path.exists(goroot_bootstrap):
            logging.info('Reusing bootstrap Go from %s', goroot_bootstrap)
            return goroot_bootstrap
    else:
        goroot_bootstrap = os.path.join(tmp_dir, subdir)
    if not echo:
        logging.info('Building Go bootstrap in %s', goroot_bootstrap)
    gohere(goroot_bootstrap, bootstrap_version, cache_root, race=False, echo=echo)
    if not echo:
        logging.info('Go bootstrap was built in %s', goroot_bootstrap)
    return goroot_bootstrap

def gohere(
    goroot,
    version,
    cache_root=None,
    test=None,
    race=True,
    echo=None,
    echo_goroot=None,
):
    if echo and not goroot:
        deps = 'bash coreutils wget tar sed gcc make'
        if version in RELOCATION_TYPE_42_VERSIONS:
            deps += ' patch'
        echo('#!/bin/bash')
        echo('# Dependencies: ' + deps)
        echo('set -xue')
        if echo_goroot:
            goroot = echo_goroot
        else:
            echo('if [ -z ${1+x} ]; then echo "Provide future GOROOT as the first argument."; exit 1; fi')
            echo('if [[ "$1" =~ ^/ ]]; then goroot="$1"; else goroot="$PWD/$1"; fi')
            goroot = '${goroot}'
    if not echo:
        goroot = os.path.abspath(goroot)
    if cache_root is None:
        cache_root = get_default_cache()
    if version not in VERSIONS:
        logging.error('Go version %s is unknown. Try --update-versions', version)
        sys.exit(1)
    if not echo and os.path.exists(goroot):
        logging.error('%s already exists. Remove it manually', goroot)
        sys.exit(1)
    goroot_bootstrap = None
    with TempDir(echo, goroot) as tmp_dir:
        bootstrap_version = is_build_with_go(version)
        if bootstrap_version:
            if not echo:
                logging.info('Go bootstrap is needed for Go %s', version)
            goroot_bootstrap = make_goroot_bootstrap(cache_root, tmp_dir, echo, bootstrap_version=bootstrap_version)
            if not echo:
                logging.info('Using Go bootstrap in %s', goroot_bootstrap)
        archive = get_from_cache_or_download(cache_root, version, tmp_dir, echo)
        unpack_file(tmp_dir, archive, echo)
        goroot_build = os.path.join(tmp_dir, 'go')
        patch_go(goroot_build, version, echo)
        build_go(goroot, goroot_build, goroot_bootstrap, test, echo)
        install_go(goroot, goroot_build, version, echo)
        if race:
            build_race(goroot, echo)
        if not echo:
            logging.info('Go %s was built and installed to %s', version, goroot)

def find_all_go_versions():
    req = urllib2.urlopen('https://golang.org/dl/')
    html = str(req.read())
    req.close()
    return set(
        match.group(1)
        for match
        in re.finditer(r'go([0-9.]+).src.tar.gz', html)
        if version_tuple(match.group(1)) >= version_tuple(MIN_VERSION_BUILT_WITH_GO)
    )

def remote_checksum(version):
    logging.info('Getting checksum of Go %s', version)
    req = urllib2.urlopen(get_url(version))
    value = checksum_of_file(req)
    req.close()
    return value

def find_checksums(versions):
    return {
        version: remote_checksum(version)
        for version in versions
    }

def update_versions():
    all_go_versions = find_all_go_versions()
    # parse this file
    this_file = sys.argv[0]
    with open(this_file) as f:
        this_file_content = f.read()
    sep1 = 'VERSIONS = {'
    sep2 = '}'
    (prefix, other) = this_file_content.split(sep1, 1)
    (known_versions_text, suffix) = other.split(sep2, 1)
    known_versions = {
        match.group(1): match.group(2)
        for match
        in re.finditer(r"'([0-9a-z.-]+)': '([0-9a-f]+)'", known_versions_text)
    }
    new_go_versions = set(all_go_versions) - set(known_versions)
    known_versions.update(find_checksums(new_go_versions))
    known_versions = sorted(
        known_versions.items(),
        key=lambda kv: version_tuple(kv[0]),
    )
    versions_text = '\n'.join(
        "    '%s': '%s'," % (version, checksum)
        for (version, checksum)
        in known_versions
    )
    with open(this_file, 'wt') as f:
        f.write(prefix + sep1 + '\n' + versions_text + '\n' + sep2 + suffix)

def printer(x):
    print(x)

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        'goroot',
        type=str,
        help='Root of Go',
        nargs='?',
    )
    group.add_argument(
        '--update-versions',
        action='store_true',
        help='Update list of Go verions instead of normal operation',
    )
    group.add_argument(
        '--echo',
        action='store_true',
        help='Produce shell code instead',
    )
    parser.add_argument(
        '--echo-goroot',
        type=str,
        help='Hardcoded GOROOT for --echo',
    )
    parser.add_argument(
        '--version',
        type=str,
        help='Go version',
        default=max(VERSIONS, key=version_tuple),
    )
    parser.add_argument(
        '--cache',
        type=str,
        help='Cache for downloaded Go sources',
        default=get_default_cache(),
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Enable Go tests (takes several minutes to complete)',
    )
    parser.add_argument(
        '--race',
        type=str,
        choices=['yes', 'no', 'auto'],
        default='auto',
        help='Whether to build std with -race',
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    if args.update_versions:
        update_versions()
        return
    if args.race == 'auto':
        race = (platform.system() != 'Windows')
    elif args.race == 'yes':
        race = True
    elif args.race == 'no':
        race = False
    goroot = args.goroot
    echo = args.echo
    if echo:
        echo = printer
    gohere(
        goroot,
        args.version,
        args.cache,
        args.test,
        race=race,
        echo=echo,
        echo_goroot=args.echo_goroot,
    )

if __name__ == '__main__':
    main()
