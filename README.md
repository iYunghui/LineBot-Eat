# LineBot 今天吃什麼

更改至
https://github.com/iYunghui/TOC-Project-2020

## Setup
### Prerequisite
* Python 3.6
* Pipenv
* LineBOT

### Install Dependency
```sh
pip3 install pipenv
pipenv --three
pipenv install
pipenv shell
```

### Run the sever

```sh
python3 app.py
```

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

![](https://i.imgur.com/DRDjsCB.jpg)
![](https://i.imgur.com/ICF7IOq.jpg)
