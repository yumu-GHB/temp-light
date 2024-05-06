#include "led.h"
#include "delay.h"
#include "key.h"
#include "sys.h"
#include "lcd.h"
#include "usart.h"	 
#include "adc.h"
#include "lsens.h"
 
/************************************************
 ALIENTEK��ӢSTM32������ʵ��19
 ���������� ʵ��     
 ����֧�֣�www.openedv.com
 �Ա����̣�http://eboard.taobao.com 
 ��ע΢�Ź���ƽ̨΢�źţ�"����ԭ��"����ѻ�ȡSTM32���ϡ�
 ������������ӿƼ����޹�˾  
 ���ߣ�����ԭ�� @ALIENTEK
************************************************/


 int main(void)
 {	 
 	u8 lesn_adcx;
	short Temprate_adcx; 
	delay_init();	    	 //��ʱ������ʼ��
	u16 adcx;
	float temp;
 	u8 t=0;	 
	u16 dacval=0;
	u8 key;
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);//�����ж����ȼ�����Ϊ��2��2λ��ռ���ȼ���2λ��Ӧ���ȼ�
	uart_init(115200);	 	//���ڳ�ʼ��Ϊ115200
	LED_Init();		  		//��ʼ����LED���ӵ�Ӳ���ӿ�
  	LCD_Init();				//��ʼ��LCD
	KEY_Init();
	Lsens_Init(); 			//��ʼ������������
	T_Adc_Init();
	Adc3_Init();

          
	while(1)
	{
		lesn_adcx=Lsens_Get_Val();
		Temprate_adcx = Get_Temprate();
		LCD_ShowxNum(30+10*8,130,lesn_adcx,3,16,0);//��ʾADC��ֵ 
		printf("Temperature:%d.%d\n",Temprate_adcx/100,Temprate_adcx%100);
		printf("Humidity:%d\n",lesn_adcx);
		LED0=!LED0;
		delay_ms(250);	
	}
}
 
