{% args data %}
<html>
    <p>Configuration was saved successfully.</p>
    <p>Your are now connected to <b>"{{ data[0] }}"</b> Wifi with ip: <b>{{ data[1] }}</b></p>
    <p>Your System is being restarted. You will be redirected to the home page in <span id="counter">15</span> second(s).</p>
</html>
<script type="text/javascript">
    function countdown() {
        var i = document.getElementById('counter');
        if (parseInt(i.innerHTML)<=0) {
            window.location.href = 'http://{{ data[1] }}/';
        }
        if (parseInt(i.innerHTML)!=0) {
            i.innerHTML = parseInt(i.innerHTML)-1;
        }
    }
    setInterval(function(){ countdown(); },1000);
</script>