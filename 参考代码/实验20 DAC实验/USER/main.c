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
 ALIENTEK精英STM32开发板实验20
 DAC 实验       
 技术支持：www.openedv.com
 淘宝店铺：http://eboard.taobao.com 
 关注微信公众平台微信号："正点原子"，免费获取STM32资料。
 广州市星翼电子科技有限公司  
 作者：正点原子 @ALIENTEK
************************************************/

 

 int main(void)
 {	 
	u16 adcx;
	float temp;
	u8 rxdata = 0;
	u8 Light_intensity;
	short Temprate_adcx; 
	delay_init();	    	 //延时函数初始化	  
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);//设置中断优先级分组为组2：2位抢占优先级，2位响应优先级
	uart_init(115200);	 	//串口初始化为115200
	KEY_Init();			  //初始化按键程序
 	LED_Init();			     //LED端口初始化
	LCD_Init();			 	 //LCD初始化
	Lsens_Init(); 			//初始化光敏传感器
	T_Adc_Init();
	Adc3_Init();
	usmart_dev.init(72);	//初始化USMART	
 	Adc_Init();		  		//ADC初始化
	Dac1_Init();				//DAC初始化
	
	DAC_SetChannel1Data(DAC_Align_12b_R, 0);//初始值为0	    	      
	while(1)
	{
		if(Serial_GetRxFlag()==1)  //读取上位机发送数据,0<rxdata<4096
		{					   
			rxdata = Serial_GetRxData();
		}
		DAC_SetChannel1Data(DAC_Align_12b_R, rxdata);
		
		Light_intensity=Lsens_Get_Val();
		Temprate_adcx = Get_Temprate();
		printf("Temperature:%d.%d\n",Temprate_adcx/100,Temprate_adcx%100);//ADC1，通道16
		printf("Light_intensity:%d\n",Light_intensity);//ADC3,通道6
		
		adcx=DAC_GetDataOutputValue(DAC_Channel_1);//读取前面设置DAC的值
		temp=(float)adcx*(3.3/4096);			//得到DAC电压值
		//printf("DAC_1:%f\n",temp);
		adcx=Get_Adc_Average(ADC_Channel_1,10);		//得到ADC转换值	  ADC2，通道1，引脚PA1
		temp=(float)adcx*(3.3/4096);			//得到ADC电压值
		//printf("DAC_2:%f\n",temp);
		
		LED0=!LED0;
		delay_ms(250);	
		
	}
 }

