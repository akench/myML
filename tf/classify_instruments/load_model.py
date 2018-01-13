import tensorflow as tf
import tensorflow.contrib.slim as slim
import numpy as np
from cv_stuff.parse_img import resize_crop, images_to_arrays, normalize_data
import pickle
import PIL.ImageOps
from PIL import Image
import glob
from matplotlib import pyplot as plt
from random import *

data_placeholder = tf.placeholder(shape = [None, 784], dtype = tf.float32)
label_placeholder = tf.placeholder(shape=[None], dtype = tf.int64)
keep_prob_placeholder = tf.placeholder(shape = (), dtype = tf.float32, name='keep_prob')

def model(net, keep_prob):
	net = tf.reshape(net, [-1, 28, 28, 1])

	with tf.variable_scope('pvg_model'):
		with slim.arg_scope([slim.conv2d], padding='SAME', weights_initializer=tf.contrib.layers.variance_scaling_initializer(uniform = False), weights_regularizer=slim.l2_regularizer(0.05)):
			with slim.arg_scope([slim.fully_connected], weights_initializer=tf.contrib.layers.variance_scaling_initializer(uniform = False), weights_regularizer=slim.l2_regularizer(0.05)):
				net = slim.conv2d(net, 20, [5,5], scope='conv1')
				net = slim.max_pool2d(net, [2,2], scope='pool1')
				net = slim.conv2d(net, 50, [5,5], scope='conv2')
				net = slim.max_pool2d(net, [2,2], scope='pool2')
				net = slim.conv2d(net, 100, [5,5], scope='conv3')
				net = slim.max_pool2d(net, [2,2], scope='pool3')
				net = slim.flatten(net, scope='flatten4')
				net = slim.fully_connected(net, 500, activation_fn = tf.nn.sigmoid, scope='fc5')
				net = slim.dropout(net, keep_prob = keep_prob, scope='dropout5')
				net = slim.fully_connected(net, 2, activation_fn=None, scope='fc6')
	return net


def make_prediction(data, is_file_path):

	if is_file_path:
		data = resize_crop(img = data, crop_type = 'center', size = 28)
		data.save('org_data/test.jpg')
		data = images_to_arrays([data])

		d = pickle.load(open('processed_data/train_data.p', 'rb'))
		_, m, std = normalize_data(d)

		data -= m
		data /= std

	prediction = model(data_placeholder, keep_prob_placeholder)

	with tf.Session() as sess:

		saver = tf.train.Saver()
		saver.restore(sess, 'out/pvg_model.chkp')

		# var = [v for v in tf.trainable_variables() if v.name == "pvg_model/conv1/weights:0"]
		# print(sess.run(var)[0][0][0][0][0])


		logits = sess.run(prediction, feed_dict={data_placeholder: data, keep_prob_placeholder: 1.0})
		logits = tf.squeeze(logits)
		logits_arr = sess.run(logits)

		print('LOGITS =', logits_arr)
		# if abs(logits_arr[0] - logits_arr[1]) < 100:
		# 	return 'neither'

		softmax_output = tf.nn.softmax(logits = logits_arr)
		probs = sess.run(softmax_output)
		n = sess.run(tf.argmax(softmax_output))

		#
		if n == 0:
			return 'piano keyboard, ' + str(probs[n])
		else:
			return 'acoustic guitar, ' + str(probs[n])
		return 'hi'



def accuracy_on_test_data(test_data, test_labels):

	prediction = model(data_placeholder, keep_prob_placeholder)

	correct = tf.equal(tf.argmax(prediction, 1), label_placeholder)
	accuracy = tf.reduce_mean(tf.cast(correct, 'float'))

	with tf.Session() as sess:

		saver = tf.train.Saver()
		saver.restore(sess, 'out/pvg_model.chkp')

		acc = accuracy.eval({data_placeholder: test_data, label_placeholder: test_labels,
							keep_prob_placeholder: 1.0})

		return acc


def create_test_data_and_labels(folder_name, label):
	paths = glob.glob('org_data/' + folder_name + '/*')
	imgs = []
	for path in paths:
		imgs.append(resize_crop(path))

	data = images_to_arrays(imgs)

	pickle.dump(data, open('processed_data/' + folder_name + '_data.p', 'wb'))

	labels = np.full(len(data), label)
	pickle.dump(labels, open('processed_data/' + folder_name + '_labels.p', 'wb'))


p = pickle.load(open('processed_data/train_data.p', 'rb'))
l = pickle.load(open('processed_data/train_labels.p', 'rb'))
_, m, s = normalize_data(p)
print(m[0:2])

p=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,6,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,9,10,10,36,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,17,52,132,189,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,3,7,0,0,0,47,129,180,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,2,10,20,23,26,57,39,9,0,0,8,0,0,0,0,0,0,0,0,0,0,0,2,7,9,5,6,0,1,17,121,183,121,65,68,56,35,40,0,0,0,0,0,0,0,0,0,0,0,1,9,20,19,14,17,45,5,0,33,115,188,153,67,52,65,62,4,0,0,0,0,0,0,1,0,0,1,5,12,27,76,148,132,113,119,21,0,0,69,170,179,98,37,58,17,0,0,0,0,0,3,5,2,0,9,47,99,143,209,220,222,130,109,140,46,2,0,55,128,178,147,62,25,0,0,0,0,2,6,14,4,0,16,101,164,191,189,209,208,219,109,106,95,0,11,0,41,170,217,198,171,2,5,1,1,12,44,104,58,0,3,1,57,163,178,194,212,210,215,99,73,14,0,0,117,220,205,210,217,9,13,1,6,57,131,207,144,4,0,2,4,97,177,171,200,206,210,212,93,28,84,138,219,213,210,210,208,44,79,4,10,40,47,168,178,50,27,8,9,39,128,173,170,213,212,219,210,193,229,219,192,213,215,210,210,160,183,5,0,22,11,124,201,89,31,30,28,8,82,199,189,185,222,212,216,219,210,213,212,197,211,215,214,140,177,20,5,19,6,84,189,136,36,32,9,7,171,221,221,179,201,221,214,214,215,213,213,212,202,216,202,120,192,73,30,30,15,60,156,190,28,15,85,170,226,216,218,214,177,217,216,215,214,218,225,218,164,103,137,113,205,98,31,51,7,45,189,222,153,119,233,227,216,218,216,221,202,187,223,221,225,201,152,101,87,72,123,106,200,131,19,27,13,158,232,215,240,168,187,223,217,218,216,215,225,197,205,193,127,91,91,112,133,111,106,101,208,144,27,85,195,226,219,219,222,201,160,226,215,218,226,226,205,134,97,134,107,127,137,136,133,129,89,176,221,198,202,193,226,219,221,220,219,222,158,211,228,219,181,129,95,101,84,137,146,137,135,134,133,139,109,218,214,219,224,188,213,222,220,219,219,235,187,176,177,109,96,110,131,145,113,117,150,134,135,139,147,142,111,211,212,212,218,186,205,220,224,232,222,186,109,82,140,129,143,145,141,139,133,98,153,143,148,135,100,48,12,210,212,212,215,189,203,228,207,160,113,95,119,88,137,151,142,141,141,138,148,109,138,128,74,29,0,0,0,208,210,214,227,190,176,156,101,104,127,144,153,121,112,155,139,142,149,152,140,91,41,16,0,0,0,1,1,216,224,212,170,97,84,142,141,151,149,146,145,142,99,155,155,150,125,77,30,3,0,0,1,1,0,0,0,192,147,104,96,125,101,138,156,147,147,147,147,157,120,124,109,51,13,0,0,0,1,1,0,0,0,0,0,97,105,133,149,155,131,112,159,147,149,150,151,134,82,25,4,0,0,1,1,0,0,0,0,0,0,0,0]

for i in range(len(p)):
	p[i] = float(p[i]) - m[i]
	p[i] = p[i] / s[i]

print(make_prediction(np.reshape(p, (1,784)), False))




# print(accuracy_on_test_data(p, l))
#
# p = p.reshape((1, 784))
# print(make_prediction(p, False))

# string ="""-0.8826487
# -0.97001565
# -1.0424411
# -1.1061375
# -1.163025
# -1.2018944
# -1.2334406
# -1.2588187
# -1.276974
# -1.291216
# -1.2986828
# -1.2813132
# -1.2587042
# -1.2330636
# -1.2127734
# -1.192836
# -1.1659192
# -1.1452584
# -1.121247
# -1.1096499
# -1.0873747
# -1.0603834
# -1.0346606
# -1.0069954
# -0.98786885
# -0.9489954
# -0.88464856
# -0.8004565
# -0.9950982
# -1.0968858
# -1.1842598
# -1.274063
# -1.3248683
# -1.3792524
# -1.4097794
# -1.4132643
# -1.4369503
# -1.4434036
# -1.4308221
# -1.4012444
# -1.369698
# -1.3334746
# -1.3044909
# -1.3015914
# -1.2863338
# -1.2739607
# -1.2564268
# -1.2343197
# -1.2026019
# -1.1812828
# -1.1522893
# -1.108936
# -1.0778844
# -1.0379099
# -0.9635401
# -0.86648494
# -1.1043153
# -1.2168763
# -1.3074411
# -1.3878331
# -1.4414508
# -1.486125
# -1.5175046
# -1.5208147
# -1.5153643
# -1.497675
# -1.4827423
# -1.4649558
# -1.4414915
# -1.39964
# -1.378014
# -1.3745822
# -1.3606454
# -1.3631792
# -1.3466614
# -1.3251938
# -1.3029461
# -1.2839352
# -1.2560947
# -1.2190231
# -1.1738205
# -1.1231838
# -1.0489122
# -0.9435636
# -1.1994495
# -1.323855
# -1.4115351
# -1.4760132
# -1.5155295
# -1.546562
# -1.5614926
# -1.5585845
# -1.5528328
# -1.5186663
# -1.5086024
# -1.4842972
# -1.4541453
# -1.4178778
# -1.3981557
# -1.4187452
# -1.407138
# -1.419742
# -1.4001659
# -1.3986491
# -1.3770547
# -1.3592306
# -1.3370552
# -1.3052303
# -1.2615991
# -1.2136791
# -1.1362239
# -1.0253987
# -1.2690479
# -1.3928857
# -1.4704045
# -1.5127435
# -1.566025
# -1.5558317
# -1.5580007
# -1.5511838
# -1.5615226
# -1.5492347
# -1.515033
# -1.4789362
# -1.4692818
# -1.4326441
# -1.4335713
# -1.4447668
# -1.4327295
# -1.4418825
# -1.4505135
# -1.4480563
# -1.4548172
# -1.4217722
# -1.4216214
# -1.3746959
# -1.320534
# -1.279602
# -1.2053946
# -1.0968299
# -1.3145436
# -1.4231067
# -1.4982015
# -1.5317271
# -1.5675389
# -1.5679435
# -1.5469033
# -1.5528592
# -1.5425146
# -1.5213685
# -1.5117131
# -1.467694
# -1.4500213
# -1.4068537
# -1.4104443
# -1.4408182
# -1.4363478
# -1.4313296
# -1.4718801
# -1.4901435
# -1.4816846
# -1.4647677
# -1.4519874
# -1.4300429
# -1.3833824
# -1.329236
# -1.2520627
# -1.1426927
# -1.3673975
# -1.4635668
# -1.5139475
# -1.5515225
# -1.5777736
# -1.5524828
# -1.5384856
# -1.5321378
# -1.5230501
# -1.5043199
# -1.4775773
# -1.4525199
# -1.4446995
# -1.3786573
# -1.3792344
# -1.4165785
# -1.437199
# -1.4287088
# -1.4592206
# -1.4840944
# -1.490109
# -1.4895917
# -1.4909686
# -1.4587798
# -1.4335483
# -1.3881551
# -1.3126745
# -1.2046094
# -1.4085286
# -1.4878528
# -1.5549942
# -1.576181
# -1.5955919
# -1.5848235
# -1.5523782
# -1.5460818
# -1.5341796
# -1.4976971
# -1.4781127
# -1.4245172
# -1.42062
# -1.3867712
# -1.3975489
# -1.4200085
# -1.4251817
# -1.4453294
# -1.4844514
# -1.5081273
# -1.5242053
# -1.5336591
# -1.5446018
# -1.5143871
# -1.4855337
# -1.4430826
# -1.3797259
# -1.2686404
# -1.4292945
# -1.507555
# -1.5641814
# -1.5975832
# -1.6110357
# -1.5992035
# -1.586262
# -1.5911962
# -1.5609821
# -1.4966682
# -1.4841521
# -1.4391253
# -1.4122446
# -1.3815602
# -1.3953274
# -1.4162313
# -1.419851
# -1.462559
# -1.4939811
# -1.5196974
# -1.5460126
# -1.5659775
# -1.5798606
# -1.5518166
# -1.5304482
# -1.5085123
# -1.4513601
# -1.3284687
# -1.4359351
# -1.5430119
# -1.5733118
# -1.6133689
# -1.633648
# -1.6258792
# -1.5987287
# -1.6052663
# -1.5683907
# -1.5210394
# -1.5148422
# -1.4830033
# -1.4501754
# -1.3951811
# -1.3966187
# -1.4291859
# -1.4531711
# -1.4880803
# -1.5202484
# -1.5347903
# -1.5649767
# -1.5606234
# -1.5750425
# -1.5872055
# -1.5552622
# -1.5242852
# -1.4849387
# -1.3660765
# -1.4673402
# -1.6028486
# -1.6408709
# -1.6927669
# -1.7099783
# -1.6964483
# -1.6406394
# -1.6442806
# -1.6455184
# -1.595009
# -1.5825593
# -1.5464671
# -1.518541
# -1.4778398
# -1.4877706
# -1.4828619
# -1.4986107
# -1.5358806
# -1.5549732
# -1.5552137
# -1.5846689
# -1.6011223
# -1.5970298
# -1.6026629
# -1.5698308
# -1.5261834
# -1.4941964
# -1.4085233
# -1.5191994
# -1.6520647
# -1.6863223
# -1.7162687
# -1.7242895
# -1.7166165
# -1.6867737
# -1.6738173
# -1.6740633
# -1.6384298
# -1.6103235
# -1.5565819
# -1.5533186
# -1.522921
# -1.5076197
# -1.5207317
# -1.5354418
# -1.5326998
# -1.5508082
# -1.5716839
# -1.6008292
# -1.6152356
# -1.599076
# -1.6169839
# -1.6070458
# -1.5713466
# -1.521221
# -1.4239622
# -1.5332271
# -1.6499953
# -1.6975112
# -1.7325885
# -1.7298557
# -1.7167416
# -1.7009313
# -1.6795608
# -1.664947
# -1.6428035
# -1.613093
# -1.5451745
# -1.5375868
# -1.5017533
# -1.5036334
# -1.5559452
# -1.5605285
# -1.5715739
# -1.5930221
# -1.6064436
# -1.622311
# -1.6377327
# -1.6249007
# -1.6529629
# -1.6372627
# -1.5987707
# -1.5709003
# -1.4624139
# -1.5359064
# -1.6507726
# -1.7095144
# -1.7798324
# -1.7683827
# -1.7485613
# -1.7561972
# -1.7251086
# -1.7024503
# -1.6777077
# -1.6365236
# -1.6190667
# -1.5725362
# -1.5253185
# -1.5335085
# -1.569198
# -1.593067
# -1.5925115
# -1.6480008
# -1.6557328
# -1.64217
# -1.6696889
# -1.6570209
# -1.6618433
# -1.6744987
# -1.618356
# -1.5895922
# -1.4879426
# -1.5539937
# -1.6726643
# -1.7303799
# -1.7669917
# -1.7847131
# -1.7688972
# -1.806217
# -1.7776833
# -1.7587982
# -1.7205125
# -1.6615674
# -1.6380963
# -1.6210977
# -1.5501702
# -1.5814385
# -1.6013196
# -1.6313685
# -1.6207005
# -1.6642101
# -1.6576682
# -1.6550233
# -1.6946813
# -1.6702343
# -1.6798629
# -1.6789532
# -1.6510904
# -1.5998381
# -1.4828961
# -1.5352534
# -1.6644161
# -1.741894
# -1.7534404
# -1.8033478
# -1.76877
# -1.830971
# -1.7973337
# -1.7885673
# -1.7217096
# -1.705671
# -1.7064235
# -1.6632091
# -1.6179811
# -1.6425335
# -1.6759671
# -1.7010171
# -1.7009484
# -1.701335
# -1.716805
# -1.6994066
# -1.7276485
# -1.7234943
# -1.712106
# -1.684121
# -1.6644851
# -1.5881263
# -1.4663236
# -1.5421158
# -1.6866558
# -1.7758093
# -1.7917144
# -1.8259448
# -1.803651
# -1.8184427
# -1.827454
# -1.8000171
# -1.7576029
# -1.7364972
# -1.7576115
# -1.705606
# -1.6452942
# -1.6351182
# -1.6702706
# -1.7064872
# -1.7246513
# -1.7281168
# -1.7553821
# -1.7532383
# -1.7643827
# -1.7540865
# -1.7507782
# -1.7195122
# -1.6785588
# -1.595261
# -1.4432381
# -1.4991752
# -1.6335969
# -1.7174906
# -1.7440182
# -1.7641965
# -1.7777034
# -1.7734056
# -1.7977961
# -1.7771413
# -1.7294505
# -1.7172617
# -1.7059672
# -1.6698492
# -1.6423286
# -1.6337351
# -1.6438279
# -1.6648343
# -1.7088953
# -1.716173
# -1.7393965
# -1.7517347
# -1.7414439
# -1.759272
# -1.7521521
# -1.715992
# -1.6721774
# -1.580334
# -1.409533
# -1.480314
# -1.6258177
# -1.7070256
# -1.767937
# -1.769091
# -1.839419
# -1.8310145
# -1.8118738
# -1.7855666
# -1.739062
# -1.724508
# -1.7247323
# -1.6648663
# -1.6240945
# -1.6493263
# -1.6647038
# -1.7076467
# -1.7240772
# -1.7298497
# -1.7493043
# -1.7936989
# -1.7963424
# -1.7994183
# -1.7800473
# -1.725041
# -1.6561332
# -1.5450182
# -1.4024494
# -1.4596235
# -1.6031845
# -1.7062949
# -1.798056
# -1.8240579
# -1.8312781
# -1.8265735
# -1.7981948
# -1.7945977
# -1.7461357
# -1.7223734
# -1.7406452
# -1.6845827
# -1.6607019
# -1.6782908
# -1.6924505
# -1.7653853
# -1.7756418
# -1.8004045
# -1.7909048
# -1.825553
# -1.8071125
# -1.8076558
# -1.782289
# -1.7139413
# -1.6276637
# -1.5103962
# -1.3749156
# -1.4371265
# -1.5912472
# -1.699789
# -1.8255695
# -1.8429819
# -1.8820615
# -1.8693342
# -1.8340288
# -1.8799026
# -1.8708515
# -1.8722736
# -1.8277725
# -1.805979
# -1.757763
# -1.7887777
# -1.7895333
# -1.8159338
# -1.8317943
# -1.8422393
# -1.8699213
# -1.8557777
# -1.8119527
# -1.7922521
# -1.7653146
# -1.6734941
# -1.581295
# -1.489174
# -1.3240184
# -1.4139283
# -1.5674518
# -1.6968232
# -1.8336076
# -1.8701903
# -1.8951125
# -1.9375696
# -1.9408565
# -1.9378802
# -1.9350958
# -1.9574376
# -1.9193995
# -1.8960325
# -1.8619906
# -1.869847
# -1.8690706
# -1.8948777
# -1.9065443
# -1.8884634
# -1.8834013
# -1.875758
# -1.8256928
# -1.7768548
# -1.7148582
# -1.6447384
# -1.5319374
# -1.4351733
# -1.2621679
# -1.3807652
# -1.5156815
# -1.6480147
# -1.7848171
# -1.8699062
# -1.9032804
# -1.9163171
# -1.9606768
# -1.9928125
# -1.9260099
# -1.9236434
# -1.9300728
# -1.919908
# -1.904598
# -1.9027276
# -1.8968196
# -1.9138417
# -1.9069464
# -1.8874437
# -1.8588681
# -1.822475
# -1.7787699
# -1.7298851
# -1.6613696
# -1.5722144
# -1.479884
# -1.3594619
# -1.2141924
# -1.3244451
# -1.458811
# -1.5722437
# -1.701559
# -1.8098205
# -1.8677329
# -1.9324522
# -1.9426956
# -1.9593139
# -1.964298
# -1.976326
# -1.9642996
# -1.9514581
# -1.9222
# -1.8943908
# -1.8685601
# -1.8787078
# -1.8699416
# -1.856607
# -1.8232222
# -1.7784443
# -1.7304734
# -1.6525245
# -1.5957965
# -1.4874842
# -1.4025793
# -1.270281
# -1.1357303
# -1.2371227
# -1.3757855
# -1.5136052
# -1.591972
# -1.6981356
# -1.782926
# -1.8351623
# -1.8859693
# -1.9278207
# -1.9341962
# -1.9161663
# -1.9334226
# -1.9406582
# -1.9070164
# -1.9312668
# -1.9044185
# -1.8886728
# -1.8482037
# -1.8292226
# -1.787126
# -1.7229266
# -1.6448004
# -1.5655524
# -1.4663548
# -1.3640826
# -1.288217
# -1.1734225
# -1.0555373
# -1.1460714
# -1.2569972
# -1.3878137
# -1.5107192
# -1.617289
# -1.6816858
# -1.741473
# -1.8086543
# -1.8699958
# -1.8925656
# -1.9074631
# -1.9147105
# -1.9050629
# -1.8838879
# -1.8933506
# -1.8657509
# -1.8352818
# -1.7662991
# -1.7043335
# -1.6344069
# -1.5728015
# -1.4826347
# -1.4023099
# -1.3108174
# -1.2599448
# -1.1939051
# -1.0748761
# -0.9631632
# -1.0189158
# -1.1014265
# -1.206599
# -1.3107861
# -1.4222187
# -1.5091339
# -1.5789981
# -1.6227888
# -1.6891487
# -1.7344162
# -1.7780746
# -1.7799804
# -1.7652081
# -1.7369282
# -1.692755
# -1.6525687
# -1.5995569
# -1.5593152
# -1.5199618
# -1.4518553
# -1.375679
# -1.3029809
# -1.2183881
# -1.1471955
# -1.0881877
# -1.0137584
# -0.92031693
# -0.84222585
# -0.8948074
# -0.9668453
# -1.0464728
# -1.1210482
# -1.2014776
# -1.2876611
# -1.3457623
# -1.4034666
# -1.4647062
# -1.4888893
# -1.4914213
# -1.5034608
# -1.4995767
# -1.4856124
# -1.4634057
# -1.4174027
# -1.369557
# -1.3171606
# -1.2558153
# -1.1969676
# -1.1393497
# -1.092878
# -1.0396773
# -0.9990479
# -0.9559447
# -0.90160775
# -0.82879364
# -0.7646363"""
#
# arr = string.split('\n')
# arr = np.reshape(arr, (1, 784))
# print(make_prediction(arr, False))
