dir=~/git/esp32
delimiter=esp32/


function usage() {
  echo $"Usage: $0 -{first_load | load_all_files}"
}

function check_loaded_files() {
    echo "Loaded Files"
    cmd="ampy -p /dev/tty.usbserial-0001 -d 1.5 ls"
    eval "$cmd"
}

function first_load() {
  for filename in $dir/*; do
    file="$(basename $filename)"
    if [ $file != "README.md" ] &&\
       [ $file != "esp32-20210902-v1.17.bin" ] &&\
       [ $file != "/Users/antonind/git/esp32/load_app_into_esp32.sh" ]; then
      cmd="ampy -p /dev/tty.usbserial-0001 -d 1.5 put $filename"
      echo "loading $filename with command: $cmd"
      eval "$cmd"
    fi
  done
  echo "loading is done"
  check_loaded_files
}

function load_all_files() {
   for f in $(find $dir -name '*.py' -o -name '*.tpl' -o -name '*.html'); do
    string=$f$delimiter

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
  check_loaded_files
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