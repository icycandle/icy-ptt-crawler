#Usage
create a settings.py file, setting ptt.cc account and password:

```python
LOGIN_INFO = {
    'user': 'YOUR_NAME',
    'passwd': 'PASSW**D',
}
```


  ANSI 顏色控制碼如下 :

    文字屬性:  Text attributes

                 0    正常屬性 ( All attributes off )
                 1    高亮度   ( Bold on )                    
                 4    底線模式 ( Underscore )  (視模擬器而定) 
                 5    閃爍     ( Blink on )                   
                 7    反相     ( Reverse video on )           

     文字顏色:  Foreground colors

                30   Black
                31   Red
                32   Green
                33   Yellow
                34   Blue
                35   Magenta
                36   Cyan
                37   White

    背景顏色:  Background colors

                40   Black                                
                41   Red                                  
                42   Green                                
                43   Yellow                               
                44   Blue                                 
                45   Magenta                              
                46   Cyan                                 
                47   White                                

# 最後記得用 *[37;40;0m 還原就好啦!!
