case $1 in
  start)
    docker build -t web_cam_bot .
    docker run web_cam_bot
  ;;
  *)
    echo "Use 'start' command"
esac