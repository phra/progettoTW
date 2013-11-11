<?php
/*

DESCRITTORE E' APERTO 
E' aperto

		input: ORARIO1, ORARIO2
		output: booleano
		crediti: 3

	Descrittore che prende in input un multiintervallo di orari 
	(ad es.: lun,mar,mer: 10:00-13:00, 15:30-20:00. gio,ven,sab: 10:00-12:30, 16:30-20:00.) 
	e un intervallo semplice (es.: mar: 9:30-11:00) 
	e verifica se la posizione del secondo orario nel primo è parzialmente interna 
	(aperto - vero) o no (chiuso - falso) 


Aprirà

    input: ORARIO1, ORARIO2
    output: semaforo a quattro valori
    crediti: 3

	Descrittore che prende in input un multiintervallo di orari (ad es.: lun,mar,mer: 10:00-13:00,
	15:30-20:00. gio,ven,sab: 10:00-12:30, 16:30-20:00.) e un intervallo semplice (es.: mar: 9:30-11:00) 
	e verifica se la posizione del secondo orario nel primo è interna (sempre aperto - verde), sovrapposto a 
	sinistra (chiuso adesso, ma aprirà - rosso/arancione), sovrapposto a destra (aperto adesso, ma chiuderà
	- arancione/verde) o esterna (sempre chiuso - rosso) 
*/

// includo le funzioni
include_once("./funzioni.php");

// ottengo i parametri
$param = ottieni_parametri_descrittore($_SERVER["REQUEST_URI"]);

$param = $param["parametri"];

// conto i parametri
$quanti = count($param);

// ci devono essere 2 parametri, altrimenti errore 406
if($quanti !== 2)
	richiesta_non_valida("Questo descrittore accetta solo due argomenti, ne hai forniti $quanti.");

// PORTO I GIORNI A MINUSCOLO
foreach($param as $i=>$p)
{
	$param[$i] = strtolower($param[$i]);
}

// se ci sono più parametri nel primo parametri li separo
$param[0] = preg_split('/(?<=\.) /', $param[0], -1, PREG_SPLIT_NO_EMPTY);

// il primo parametro deve essere un orario
foreach($param[0] as $parametro)
	if(!is_orario($parametro, "OPENING"))
		richiesta_non_valida("Il primo parametro non e' un orario valido. Controlla il protocollo.");
// il secondo deve essere un orario semplice.
if(!is_orario($param[1], "SEMPLICE"))
	richiesta_non_valida("Il secondo parametro non e' un orario semplice valido. Controlla il protocollo.");	

// compatto tutti gli elementi del primo parametro in un unica variabile
foreach($param[0] as $primo)
{
	$primoparametro[] = split_orario($primo);
}

// split del secondo parametro
$secondoparametro = split_orario_semplice($param[1]);

//debug_stamp($primoparametro);

// controllo se la location è aperta o chiusa
$risultato = confronta_orari($primoparametro, $secondoparametro);

// se è stato chiesto il descrittore #3 ritorno tutti i valori, altrimenti solo 0 o 1
$nome_descrittore = nome_descrittore($_SERVER["REQUEST_URI"]);

if($nome_descrittore == "eaperto")
{
	if($risultato == 4)
		// se è aperto ritorno 1
		echo 1;
	else 
		// se non è aperto ritorno 0
		echo 0;
}
else
	// se posso ritornare un semaforo ritorno il vero valore
	echo $risultato;

//debug_stamp($param);
//debug_stamp($primoparametro);
//debug_stamp($secondoparametro);

?>
