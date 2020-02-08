# LineBot 今天吃什麼

## Finite State Machine
![fsm](https://i.imgur.com/1FnqOuf.png)

## States

* user
  * search：搜尋餐廳
    * showsearch：顯示餐廳資料
    * searcherror：若輸入的餐廳不在資料中，詢問是否要貢獻餐廳資料
  * choose：推薦餐廳
    * eat：輸入位置，依位置顯示推薦的餐廳資料
  * contribute：貢獻餐廳資料
    * upload：依照格式上傳餐廳資料
