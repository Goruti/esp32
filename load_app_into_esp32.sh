dir=~/git/esp32

function usage() {
  echo $"Usage: $0 -{first_load|load_all_files|}"
}

function first_load() {
  for filename in $dir/*; do
    if [ $filename != "/Users/diego/git/esp32/README.md" ] &&\
       [ $filename != "/Users/diego/git/esp32/load_app_into_esp32.sh" ]; then
      cmd="ampy -p /dev/tty.usbserial-0001 -d 1.5 put $filename"
      echo "loading $filename with command: $cmd"
      eval "$cmd"
    fi
  done
  echo "loading is done"
  chek_loaded_files
}

function load_all_files() {
   for f in $(find $dir -name '*.py'); do
    string=$f$dir/
    myarray=()
    while [[ $string ]]; do
      myarray+=( "${string%%"$delimiter"*}" )
      string=${string#*"$delimiter"}
    done
    cmd="ampy -p /dev/tty.usbserial-0001 -d 1.5 put $f ${myarray[*]: -1}"
      echo "loading $f with command: $cmd"
      eval "$cmd"
  done
  echo "loading is done"
  chek_loaded_files
}

function chek_loaded_files() {
    echo "Loaded Files"
    cmd="ampy -p /dev/tty.usbserial-0001 -d 1.5 ls"
    eval "$cmd"
}

while [ "$1" != "" ]; do
    case $1 in
        -first_load)
              first_load
              exit
              ;;
        -load_all_files)
              load_all_files
              exit
              ;;
        -h | --help)
              usage
              exit
              ;;
        *)
              usage
              exit 1
    esac
done