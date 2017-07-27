cbrWebService
=============

Обёртка soap-сервиса ЦБ РФ для получения справочной информации по кредитным организациям.

Как пользоваться
----------------
Скачиваем архив, распаковываем каталог "cbrWebService" и импортируем его как модуль:

.. code:: python

	from cbrWebService import cbrWebService, analytics
	cbr = cbrWebService.CreditOrgInfo()
	print(help(cbr)) #help по функциям
	print(cbr.LastUpdate())
	#analysis module
	a_metrics = analytics.Metrics()
	print(help(a_metrics)) #help по функциям
	# 1 аргумент - номера лицензий банков, 2 и 3 - даты отчётности формы 101 "с" и "по"
	# возвращается объект pandas.DataFrame()
	data_frame = a_metrics.investments_in_shares(['1326', '1481'], '2017-06-01', '2017-07-01')
