#!/bin/tclsh

set FILENAME "/etc/config/addons/www/phonemuter/pjsip.cfg"

set sip_id {}
set registrar {}
set realm {}
set username {}
set password {}

array set args { command INV sip_id 0 registrar 0 realm 0 username 0 password 0 }

proc parseQuery { } {
	global args env
	
	set query [array names env]
	if { [info exists env(QUERY_STRING)] } {
		set query $env(QUERY_STRING)
	}
	
	foreach item [split $query &] {
		if { [regexp {([^=]+)=(.+)} $item dummy key value] } {
			set args($key) $value
		}
	}
}

proc fromUTF8 { value } {
  return [string map {
    "%20" ""
    "%21" "!"
    "%23" "#"
    "%24" "$"
    "%25" "%"
    "%26" "&"
    "%27" "'"
    "%28" "("
    "%29" ")"
    "%2A" "*"
    "%2B" "+"
    "%2C" ","
    "%2D" "-"
    "%2E" "."
    "%2F" "/"
    "%3A" ":"
    "%3B" ";"
    "%3C" "<"
    "%3D" "="
    "%40" "@"
    "%C3%84" "Ä"
    "%C3%96" "Ö"
    "%C3%9C" "Ü"
    "%C3%9F" "ß"    
    "%C3%A4" "ä"
    "%C3%B6" "ö"
    "%C3%BC" "ü" 
  } $value]
}


proc loadFromFile { filename } {
  set content ""
  catch  {
    set fd [open $filename r]
    set content [read $fd]
    close $fd
  }
  return $content
}


proc loadConfigFile { } {
	global FILENAME sip_id registrar realm username password
	
	array set content {}
	catch { array set content [loadFromFile $FILENAME] }
	
	set sip_id $content(--id)
	set registrar $content(--registrar)
	set realm $content(--realm)
	set username $content(--username)
	set password $content(--password)
}

proc saveConfigFile { } {
	global FILENAME args
	
	set fd [open $FILENAME w]
	puts $fd "--id [fromUTF8 $args(sip_id)]"
	puts $fd "--registrar [fromUTF8 $args(registrar)]"
	puts $fd "--realm [fromUTF8 $args(realm)]"
	puts $fd "--username [fromUTF8 $args(username)]"
	puts $fd "--password [fromUTF8 $args(password)]"
	close $fd
}

parseQuery
if { $args(command) == "save" } {
	saveConfigFile
	catch { close [open "|/etc/config/rc.d/phone-muter restart"] }
} 

loadConfigFile


set content [loadFromFile index.template.html]
regsub -all {<%sip_id%>} $content $sip_id content
regsub -all {<%registrar%>} $content $registrar content
regsub -all {<%realm%>} $content $realm content
regsub -all {<%username%>} $content $username content
regsub -all {<%password%>} $content $password content

puts "Content-type: text/html\n"
puts $content
