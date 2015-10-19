#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import glob
import time
import MySQLdb
import datetime
import sys

import subprocess
hangi_port=subprocess.check_output('dmesg|grep ttyUSB', shell=True)[-5:-1]



import serial
#port=serial.Serial("/dev/ttyUSB0",9600,timeout=2)
port=serial.Serial("/dev/tty"+hangi_port,9600,timeout=2)

port.flushInput()

db = MySQLdb.connect("localhost","root","root","test_zo" )
cursor = db.cursor()
#DHT11 = 11
t=0
h=0


#############---- HTML İÇİN

sayfa="""  <html>
  <head>
	<script type="text/javascript"
		  src="https://www.google.com/jsapi?autoload={
			'modules':[{
			  'name':'visualization',
			  'version':'1',
			  'packages':['corechart']
			}]
		  }"></script>

	<script type="text/javascript">
	  google.setOnLoadCallback(drawChart);

	  function drawChart() {
		var data = google.visualization.arrayToDataTable([
		  ['Zaman', 'Sicaklik', 'Nem'],"""

######################################################################

def google_chart_olustur(satirlar):
	
	table2=""
	try:
		for satir in satirlar:
			table2=table2+"['"+str(satir[1])+"',"+str(satir[2])+","+str(satir[3])+"],"
		return table2
	
	except e:
		print e,"Dongu yemedi"    
		
######################################################################		
		
kayit_mekani=raw_input("Kayit yapilan yeri giriniz: ")
sayfa2="""
				]);
		var options = {
		  title: '%s',
		  curveType: 'function',
		  legend: { position: 'bottom' }
		};

		var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));

		chart.draw(data, options);
	  }
	</script>
  </head>
  <body>
	<div id="curve_chart" style="width: 900px; height: 500px"></div>
  </body>
</html>

				"""%(kayit_mekani)

######################################################################

tablo="""<table border='1'>
						<tr>
						<th>Zaman</th>
						<th>Sicaklik</th>
						<th>Nem</th>
						</tr>"""

######################################################################

def deger_html(zaman,dt,dh):
	baslik="<h1>KUCUKAGAOGLU DATA</h1><br>"
	html_zaman="<p>Zaman: "+str(zaman)+"</p><br>"""
	html_sicaklik="<p>Sicaklik: "+str(dt)+" C</p><br>"
	html_nem="<p>Nem: "+str(dh)+" %Rh</p><br>"


def nem_sicaklik_sor():
	port.write("55")	
	
def nem_sicaklik_satiri():
	return 	port.readline()
	
def bekle(tt):
	time.sleep(tt)
	
	
def tablo_olustur(satirlar):				
	
	tablo="" #bu çok önemli!!!
	for satir in satirlar:
		tablo=tablo+"<tr><td>"+str(satir[0])+"</td><td>"+str(satir[1])+"</td><td>"+str(satir[2])+"</td></tr>"

	return tablo	
	

def	veritabanina_ekle(yers,par1,par2):
				
	sql = "INSERT INTO logger(yer,zaman,isi,nem) VALUES ('"+yers+"',now(),"+str(float(par1))+","+str(float(par2))+")"
						#        sql = "INSERT INTO logger(zaman,isi,nem) VALUES (now(),22.5,44.5)"	
 	
	try:
   # Execute ile SQL kodlarını çalıştırıyoruz.
		cursor.execute(sql)
   # Commit ile veritabanında değişikleri gerçekleştiriyoruz.
		db.commit()
		print "VERITABANINA EKLENDI!!!"
	except:
   # Hata olursa işlemleri geri al
		db.rollback()	
		
		
def acilis():

	global sensor_hatasi
	sensor_hatasi=0
	global olcum  
	olcum=0 
	global ort_sicaklik
	ort_sicaklik=0
	global ort_nem
	ort_nem=0
	global toplam_sicaklik
	toplam_sicaklik=0
	global toplam_nem
	toplam_nem=0 
	global olcum_adedi
	global bekleme_suresi
	
	
	print "**************************************************"
	olcum_adedi=input("Her Kayit Oncesi Kac olcum alinsin?")	
	print "**************************************************"
	bekleme_suresi=input("Her Kayit Arasi Kac Saniye Beklensin?")
	print "**************************************************"				
	
def satirlari_cek(a):
	
	sorgu="SELECT * FROM (SELECT * FROM logger ORDER BY zaman DESC LIMIT "+str(a)+") sub ORDER BY zaman ASC"
	cursor.execute(sorgu)				
	satirlar= cursor.fetchall()	
	return satirlar
	
def anadongu():
	
	#acilis()
	sensor_hatasi=0
	olcum=0  
	ort_sicaklik=0
	ort_nem=0
	
	toplam_sicaklik=0
	toplam_nem=0 
	
	print "**************************************************"
	olcum_adedi=input("Her Kayit Oncesi Kac olcum alinsin?")	
	print "**************************************************"
	bekleme_suresi=input("Her Kayit Arasi Kac Saniye Beklensin?")
	print "**************************************************"	
	gosterilen_sayisi=input("Grafikte kac adet veri gosterilsin?")
	print "**************************************************"
	


	# TEMELDE DONEN DONGU
	while True:		
		try:		
			nem_sicaklik_sor()			
			arduino_yanit=nem_sicaklik_satiri()	#	Nem:40.00 Sic:23.00				
					
			#ZAMANI AL
			zaman=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			#ANLIK NEM'i AL
			anlik_nem=arduino_yanit[4:9]  #string icerisinden nem alinmakta
			#ANLIK SICAKLIGI AL
			anlik_sicaklik=arduino_yanit[14:19] #string icerisinden sicaklik alinmakta
			#KAÇINCI ÖLÇÜM
			olcum=olcum+1
			#EKRANA BAS
			print zaman,anlik_sicaklik,anlik_nem,"olcum=[",olcum,"/",olcum_adedi,"]"
			
			#ORTALAMALARI BUL	
			toplam_sicaklik=toplam_sicaklik+ float(anlik_sicaklik)
			toplam_nem=toplam_nem+float(anlik_nem)
			
			#BEKLE
			bekle(bekleme_suresi)
			

			#YETERİ KADAR ÖLÇÜM ALDIM!					
			if(olcum>=olcum_adedi):
				ort_sicaklik=toplam_sicaklik/olcum_adedi
				ort_nem=toplam_nem/olcum_adedi
				dt=str(float(ort_sicaklik)).replace('.',',')
				dh=str(float(ort_nem)).replace('.',',')
					
				values2 = [zaman,dt,dh]         
				
				##--VERİTABANINA EKLE
				
				veritabanina_ekle(kayit_mekani,ort_sicaklik,ort_nem)
				
				print values2, " eklendi..."	
				
						
				table2=""		
				
				#sorgu="""SELECT * FROM (
						#SELECT * FROM logger ORDER BY zaman DESC LIMIT 50
					#) sub
					#ORDER BY zaman ASC"""				
				#cursor.execute(sorgu)				
				#satirlar= cursor.fetchall()	
				
				
				satirlar=satirlari_cek(gosterilen_sayisi)
							
				###----HTML TABLO YAPISI OLUŞTURULMAKTA
				tablo=tablo_olustur(satirlar)
				
				###----GOOGLECHART İÇİN TABLO YAPISI OLUŞTURULMAKTA		  
				google_chart_kodlari=google_chart_olustur(satirlar)
				google_chart_sayfa_kodlari=	sayfa+google_chart_kodlari+sayfa2			
				######################

				###--APACHE SERVER DAKİ index.html DOSYA İŞLEMLERİ-----
				dosya=open(r"/var/www/index.html","w")
				dosya.write(google_chart_sayfa_kodlari)	
				dosya.close()
				
				
	
				## --SAYACLARIN HEPSINI SIFIRLA!
				olcum=0
				toplam_sicaklik=0
				toplam_nem=0
				
			##-- EGER DAHA TOPLAM ÖLÇÜM ADEDİNE ULAŞILMAMIŞSA DEVAM ET	
			else:
				pass		
							
		except ValueError,e:
			
			sensor_hatasi=sensor_hatasi+1
			print "Sensor okunamadı!.",e,"hata[",sensor_hatasi,"]"			
				
		
		except KeyboardInterrupt:
			db.close()
			print "DB kapatıldı"
			sys.exit("Sistem kapatildi")
		
		except e:
			print "append olamadi"
			e=sys.exc_info()
			print e
		
		
if __name__=="__main__":	

	anadongu()
