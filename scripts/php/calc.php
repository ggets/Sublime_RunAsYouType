<?php
$c="";
while(!feof(STDIN))$c.=fgets(STDIN);
$a=explode(";",$c);
foreach($a as $v){
	if($v){
		$v=preg_replace('/\s+/','',$v);
		if(!strlen($v))echo $v;
		else eval("echo ({$v});");
		echo (';'.PHP_EOL);
	}
}