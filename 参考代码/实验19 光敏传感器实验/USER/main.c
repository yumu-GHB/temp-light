#include "led.h"
#include "delay.h"
#include "key.h"
#include "sys.h"
#include "lcd.h"
#include "usart.h"	 
#include "adc.h"
#include "lsens.h"
 
/************************************************
 ALIENTEK精英STM32开发板实验19
 光敏传感器 实验     
 技术支持：www.openedv.com
 淘宝店铺：http://eboard.taobao.com 
 关注微信公众平台微信号："正点原子"，免费获取STM32资料。
 广州市星翼电子科技有限公司  
 作者：正点原子 @ALIENTEK
************************************************/


 int main(void)
 {	 
 	u8 lesn_adcx;
	short Temprate_adcx; 
	delay_init();	    	 //延时函数初始化
	u16 adcx;
	float temp;
 	u8 t=0;	 
	u16 dacval=0;
	u8 key;
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);//设置中断优先级分组为组2：2位抢占优先级，2位响应优先级
	uart_init(115200);	 	//串口初始化为115200
	LED_Init();		  		//初始化与LED连接的硬件接口
  	LCD_Init();				//初始化LCD
	KEY_Init();
	Lsens_Init(); 			//初始化光敏传感器
	T_Adc_Init();
	Adc3_Init();

          
	while(1)
	{
		lesn_adcx=Lsens_Get_Val();
		Temprate_adcx = Get_Temprate();
		LCD_ShowxNum(30+10*8,130,lesn_adcx,3,16,0);//显示ADC的值 
		printf("Temperature:%d.%d\n",Temprate_adcx/100,Temprate_adcx%100);
		printf("Humidity:%d\n",lesn_adcx);
		LED0=!LED0;
		delay_ms(250);	
	}
}
 
