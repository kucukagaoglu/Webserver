#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import glob
import time
import MySQLdb
import datetime
import sys





import serial




port=serial.Serial("/dev/ttyUSB5",9600,timeout=2)
port.flushInput()

db = MySQLdb.connect("localhost","root","root","test_zo" )
cursor = db.cursor()
#DHT11 = 11
t=0
h=0

	
def anadongu():
	

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

	while True:
		
		#baglan()
	
		try:
		
			port.write("55")
			time.sleep(1)  	
			a=port.readline()				
			print a
			
			

			zaman=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			
			h=a[4:9]  #string icerisinden nem alinmakta
			t=a[14:19] #string icerisinden sicaklik alinmakta
			
			
				
			toplam_sicaklik=toplam_sicaklik+ float(t)
			toplam_nem=toplam_nem+float(h)
			olcum=olcum+1
			print zaman,t,h,"olcum=[",olcum,"/",olcum_adedi,"]"
			
			time.sleep(bekleme_suresi)
			
			
		   # print t,h,olcum
			#svalues = [zaman,t, h]   
							   
			if(olcum>=olcum_adedi):
				ort_sicaklik=toplam_sicaklik/olcum_adedi
				ort_nem=toplam_nem/olcum_adedi
				dt=str(float(ort_sicaklik)).replace('.',',')
				dh=str(float(ort_nem)).replace('.',',')
					
				values2 = [zaman,dt,dh]         
		  #  print c   


				print values2, " eklendi..."	
				

				
				tablo="""<table border='1'>
						<tr>
						<th>Zaman</th>
						<th>Sicaklik</th>
						<th>Nem</th>
						</tr>"""
						
				table2=""		
				
				cek="""SELECT * FROM (
						SELECT * FROM logger ORDER BY zaman DESC LIMIT 50
					) sub
					ORDER BY zaman DESC"""
				
				cursor.execute(cek)
				
				satirlar= cursor.fetchall()
				
				table=""
				
				try:
					for satir in satirlar:
						table=table+"<tr><td>"+str(satir[0])+"</td><td>"+str(satir[1])+"</td><td>"+str(satir[2])+"</td></tr>"
				except e:
					print e,"Dongu yemedi"
				
				baslik="<h1>KUCUKAGAOGLU DATA</h1><br>"
				html_zaman="<p>Zaman: "+str(zaman)+"</p><br>"""
				html_sicaklik="<p>Sicaklik: "+str(dt)+" C</p><br>"
				html_nem="<p>Nem: "+str(dh)+" %Rh</p><br>"
				
				dosya=open(r"/var/www/index.html","w")
				
				#####################
				
				
				
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
		  
		  
	 			try:
					for satir in satirlar:
						table2=table2+"['"+str(satir[0])+"',"+str(satir[1])+","+str(satir[2])+"],"
				except e:
					print e,"Dongu yemedi"     
				
				sayfa2="""
				]);
		var options = {
		  title: 'Kucukagaogullari Ev Sicaklik&Nem',
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

				"""
				
				
				
				######################
				
				
				
				#dosya.write(baslik+html_zaman+html_sicaklik+html_nem)	
#				dosya.write(baslik+tablo+table+"</table>")	
				dosya.write(sayfa+table2+sayfa2)	
				dosya.close()
				
				table2=""
				#DB isleme

								
				vt=float(ort_sicaklik)
				vh=float(ort_nem)

				print vt,vh
				
				sql = "INSERT INTO logger(zaman,isi,nem) VALUES (now(),"+str(vt)+","+str(vh)+")"
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

# Veritabanından çıkış yap
				#db.close()	




		
				## HEPSINI SIFIRLA!
				olcum=0
				toplam_sicaklik=0
				toplam_nem=0
			else:
				pass		
							
		except ValueError,e:
			
			sensor_hatasi=sensor_hatasi+1
			print "Sensor okunamadı!.",e,"hata[",sensor_hatasi,"]"			
				
		
		except KeyboardInterrupt:
			db.close()
			print "DB kapatıldı"
			sys.exit("Sistem kapatildi")
		
		except:
			print "append olamadi"
			e=sys.exc_info()
			print e
		
		
if __name__=="__main__":	

	anadongu()

