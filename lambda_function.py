import boto3
import pyminizip
import tempfile
import os

def lambda_handler(event, context):

  filename = 'myface.png' # 圧縮対象ファイル名
  tmpdir = tempfile.TemporaryDirectory() # 作業用一時ディレクトリ
  zipFilePath = tempfile.mkstemp(suffix='.zip')[1] # 一時ファイルを生成し、絶対パスを変数に代入(圧縮後のアップロード対象ファイルになる)

  print(zipFilePath)

  target_object = "" # 圧縮対象ファイル詳細情報
  s3 = boto3.resource('s3') # s3インスタンス生成

  # オブジェクトの詳細情報を取得
  target_object = s3.Object('sample-zip-bucket01', filename).get()

  # 圧縮対象のファイルを読み取り、実行環境へ書き込み(コピー)
  with open(f'{tmpdir.name}/{filename}', 'wb') as fp: # 開くファイルはこの瞬間に作成している(作成時空ファイル) ※一時ディレクトリ直下に作成
    fp.write(target_object['Body'].read()) # S3のオブジェクトを一時ファイルに書き込み

  # コピーしたファイルを暗号化
  os.chdir(tmpdir.name) # カレントディレクトリをファイルを生成したディレクトリへチェンジ
  pyminizip.compress(filename, '', zipFilePath , 'password' , 0) # 圧縮

  # S3へアップロード
  s3.Object('sample-zip-bucket02', f'{filename}.zip').put(
    Body=open(zipFilePath, 'rb')
  )

  tmpdir.cleanup() # 一時ディレクトリクリーンアップ
  os.unlink(zipFilePath) # ファイルを削除
