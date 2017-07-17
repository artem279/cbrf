# cbrWebService
Обёртка для soap-сервиса ЦБ РФ для получения справочной информации по кредитным организациям.

Как пользоваться
----------------
Скачиваем архив, распаковываем каталог "cbrWebService" и импортируем его как модуль:

.. code:: python

	from cbrWebService import cbrWebService
	print(help(cbr)) #help по функциям
	cbr = cbrWebService.CreditOrgInfo()
	print(cbr.LastUpdate())
