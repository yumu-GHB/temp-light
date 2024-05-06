#include "led.h"
#include "delay.h"
#include "key.h"
#include "sys.h"
#include "lcd.h"
#include "usart.h"	 	 
#include "dac.h"
#include "adc.h"
#include "usmart.h"
#include "usmart_str.h"	
 
 
/************************************************
 ALIENTEK��ӢSTM32������ʵ��20
 DAC ʵ��       
 ����֧�֣�www.openedv.com
 �Ա����̣�http://eboard.taobao.com 
 ��ע΢�Ź���ƽ̨΢�źţ�"����ԭ��"����ѻ�ȡSTM32���ϡ�
 ������������ӿƼ����޹�˾  
 ���ߣ�����ԭ�� @ALIENTEK
************************************************/

 

 int main(void)
 {	 
	u16 adcx;
	float temp;
	u8 rxdata = 0;
	u8 Light_intensity;
	short Temprate_adcx; 
	delay_init();	    	 //��ʱ������ʼ��	  
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);//�����ж����ȼ�����Ϊ��2��2λ��ռ���ȼ���2λ��Ӧ���ȼ�
	uart_init(115200);	 	//���ڳ�ʼ��Ϊ115200
	KEY_Init();			  //��ʼ����������
 	LED_Init();			     //LED�˿ڳ�ʼ��
	LCD_Init();			 	 //LCD��ʼ��
	Lsens_Init(); 			//��ʼ������������
	T_Adc_Init();
	Adc3_Init();
	usmart_dev.init(72);	//��ʼ��USMART	
 	Adc_Init();		  		//ADC��ʼ��
	Dac1_Init();				//DAC��ʼ��
	
	DAC_SetChannel1Data(DAC_Align_12b_R, 0);//��ʼֵΪ0	    	      
	while(1)
	{
		if(Serial_GetRxFlag()==1)  //��ȡ��λ����������,0<rxdata<4096
		{					   
			rxdata = Serial_GetRxData();
		}
		DAC_SetChannel1Data(DAC_Align_12b_R, rxdata);
		
		Light_intensity=Lsens_Get_Val();
		Temprate_adcx = Get_Temprate();
		printf("Temperature:%d.%d\n",Temprate_adcx/100,Temprate_adcx%100);//ADC1��ͨ��16
		printf("Light_intensity:%d\n",Light_intensity);//ADC3,ͨ��6
		
		adcx=DAC_GetDataOutputValue(DAC_Channel_1);//��ȡǰ������DAC��ֵ
		temp=(float)adcx*(3.3/4096);			//�õ�DAC��ѹֵ
		//printf("DAC_1:%f\n",temp);
		adcx=Get_Adc_Average(ADC_Channel_1,10);		//�õ�ADCת��ֵ	  ADC2��ͨ��1������PA1
		temp=(float)adcx*(3.3/4096);			//�õ�ADC��ѹֵ
		//printf("DAC_2:%f\n",temp);
		
		LED0=!LED0;
		delay_ms(250);	
		
	}
 }

