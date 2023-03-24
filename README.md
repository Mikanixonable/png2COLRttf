# png2COLRttf  
a wee tool to build colr font from png image  
png画像からCOLRカラーフォント規格のttfファイルを出力するpythonコード  
1.pyは画像処理AIに入力する文字の画像を書き出すコード、2.pyは画像からフォントを出力するコード
  
#依存  
cmd用にパスを通すもの: potrace,nanoemoji  
pythonライブラリ: pillow,cv2,lxml  
  
#準備  
##anaconda https://www.anaconda.com/ pythonを動かす環境を作るのに使う  
ダウンロードしてインストールしpathを通す。windows10の場合  
設定>システム>詳細情報>システムの詳細設定>環境変数(N)>ユーザーの環境変数>編集(E)>新規  
から「C:\Users\UserName\anaconda3\Scripts」などとanacondaのあるフォルダを入力しOKを押す  
  
##potrace https://potrace.sourceforge.net/#downloading 画像をトレースしてsvgにするのに使う
ダウンロードしpathを通す。windows10の場合  
設定>システム>詳細情報>システムの詳細設定>環境変数(N)>ユーザーの環境変数>編集(E)>新規
から「C:\p\potrace」などとpotrace.exeのあるフォルダを入力しOKを押す
 
##nanoemoji https://github.com/googlefonts/nanoemoji svgからカラーフォントを作るのに使う  
win+rから出る入力フォームにcmdと書いてcmdを起動する。pip install nanoemojiと打ってインストールする  
  
##pillow  
cmdからpip install pillowと打ってインストールする  

##cv2  
cmdからpip install cv2と打ってインストールする  
  
#lxml  
cmdからpip install lxmlと打ってインストールする  
  
#実行  
##1.pyの実行  
JIS.txtにフォントに入れる文字を入れる  
1.pyのfont_file = r'.\SourceHanSerif-Heavy.otf'のところを自分の持っているフォントファイルの位置に置き換える  
cmdを起動し、cdコマンドで1.pyのあるフォルダに移動し、python 1.pyと打って実行  
txtファイルにある文字が一つずつ画像に吐き出される  
  
##2.pyの実行  
コード中の
colorDic = {  
    "main": "#111111",  
    "c1":"#19285D",  
    "c2":"#465850",  
    "c3":"#0E5E3F",  
  
    "back": "#FFFFFF"  
}  
の箇所にフォントに入れたい色コードを入れる。backの色は特別で背景としてカウントされフォントには入らない  
2.pyをフォントにしたいpng画像(uni2367のようなファイル形式)があるフォルダに入れる  
cmdを起動し、cdコマンドで2.pyのあるフォルダに移動し、python 2.pyと打って実行  
3000文字くらいだと2時間以上かかるので気長に待つ。固まって動かないように見えることもあるが、再びC: >のような表示が出るまで触らずに待つ  
test1.ttfという名前のカラーフォントがbuildフォルダの中に作成される。フォント名を変えたいときは、コード中のfontname = "test1"の部分を書き換える。  
  
#png2ttf  
[png2ttf](https://github.com/Mikanixonable/png2ttf)  
姉妹プログラム。こっちは画像から普通の白黒フォントを自動生成する
