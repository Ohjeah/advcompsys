sources=/home/mq/Downloads/website/advances
webpy=/home/mq/Work/repo/advcompsys
cd $sources
lektor build -O	tmp
cp tmp/index.html $webpy/templates/.
cp tmp/static/* $webpy/static/.
cd tmp
for D in `find . -type d`; do
	cp $D/index.html $webpy/templates/$D.html
done
rm $webpy/templates/tmp.html
sed -i '1s/^/$def with(form)\n /' $webpy/templates/registration.html
