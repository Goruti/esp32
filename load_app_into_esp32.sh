for filename in ~/git/esp32/*; do
  if [ $filename != "/Users/diego/git/esp32/README.md" ] &&\
     [ $filename != "/Users/diego/git/esp32/load_app_into_esp32.sh" ]; then
    cmd="ampy -p /dev/tty.usbserial-0001 -d 1.5 put $filename"
    echo "loading $filename with command: $cmd"
    eval "$cmd"
    sleep 1
  fi
done
echo "loading has been finished"
cmd="ampy -p /dev/tty.usbserial-0001 -d 1.5 ls"
eval "$cmd"
