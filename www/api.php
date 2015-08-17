<?php
/*
    API Demo, http://markroland.com/blog/restful-php-api/
 
    This script provides a RESTful API interface for a web application
 
    Input:
 
        $_GET['format'] = [ json | html | xml ]
        $_GET['method'] = []
 
    Output: A formatted HTTP response
 
    Author: Mark Roland
 
    History:
        11/13/2012 - Created
 
*/
 
// --- Step 1: Initialize variables and functions
error_reporting(E_ALL);
//error_reporting(0);

//set default:
if (isset($_REQUEST['format']))
  $format = $_REQUEST['format'];
else
  $format = 'json';
if ((!($format)) or (!in_array(strtolower($format),['json','xml']))) $format = 'json';
 
/**
 * Deliver HTTP Response
 * @param string $format The desired HTTP response content type: [json, html, xml]
 * @param string $api_response The desired HTTP response data
 * @return void
 **/
function deliver_response($format, $api_response){
 
    // Define HTTP responses
    $http_response_code = array(
        200 => 'OK',
        400 => 'Bad Request',
        401 => 'Unauthorized',
        403 => 'Forbidden',
        404 => 'Not Found'
    );
   
 
    // Set HTTP Response
    header('HTTP/1.1 '.$api_response['status'].' '.$http_response_code[ $api_response['status'] ]);
 
    // Process different content types
    if( strcasecmp($format,'json') == 0 ){
 
        // Set HTTP Response Content Type
        header('Content-Type: application/json; charset=utf-8');
 
        // Format data into a JSON response
        $json_response = json_encode($api_response);
 
        // Deliver formatted data
        echo $json_response;
 
    }elseif( strcasecmp($format,'xml') == 0 ){
 
        // Set HTTP Response Content Type
        header('Content-Type: application/xml; charset=utf-8');
 
        // Format data into an XML response (This is only good at handling string data, not arrays)
        $xml_response = '<?xml version="1.0" encoding="UTF-8"?>'."\n".
            '<response>'."\n".
            "\t".'<code>'.$api_response['code'].'</code>'."\n".
            "\t".'<data>'.$api_response['data'].'</data>'."\n".
            '</response>';
 
        // Deliver formatted data
        echo $xml_response;
 
    }else{
 
        // Set HTTP Response Content Type (This is only good at handling string data, not arrays)
        header('Content-Type: text/html; charset=utf-8');
 
        // Deliver formatted data
        echo $api_response['data'];
 
    }
 
    // End script process
    exit;
 
}
 
// Define whether an HTTPS connection is required
$HTTPS_required = FALSE;
 
// Define whether user authentication is required
$authentication_required = TRUE;
 
// Define API response codes and their related HTTP response
$api_response_code = array(
    'unknown_error' => array('HTTP Response' => 400, 'Message' => 'Unknown Error'),
    'success' => array('HTTP Response' => 200, 'Message' => 'Success'),
    'https_required' => array('HTTP Response' => 403, 'Message' => 'HTTPS Required'),
    'authentication_required' => array('HTTP Response' => 401, 'Message' => 'Authentication Required'),
    'authentication_failed' => array('HTTP Response' => 401, 'Message' => 'Authentication Failed'),
    'invalid_request' => array('HTTP Response' => 404, 'Message' => 'Invalid Request'),
    'invalid_response_format' => array('HTTP Response' => 400, 'Message' => 'Invalid Response Format')
);
 
// Set default HTTP response to unknown_error 'ok'
$response['code'] = 'unknown_error';
$response['status'] = 400;
$response['data'] = null;

// --- Step 2: Authorization
include_once("secret.php");
if( $authentication_required ){
    
    if( empty($_REQUEST['key'])){
        $response['code'] = 'authentication_required';
        $response['status'] = $api_response_code[ $response['code'] ]['HTTP Response'];
        $response['data'] = $api_response_code[ $response['code'] ]['Message'];
 
        // Return Response to browser
        deliver_response($format, $response);
    }
 
    // Return an error response if user fails authentication. This is a very simplistic example
    // that should be modified for security in a production environment
    elseif( $_REQUEST['key'] != $secret['key']){
        $response['code'] = 'authentication_failed';
        $response['status'] = $api_response_code[ $response['code'] ]['HTTP Response'];
        $response['data'] = $api_response_code[ $response['code'] ]['Message'];
 
        // Return Response to browser
        deliver_response($format, $response);
    }   
}
// --- Step 3: Process Request
if (!isset($_REQUEST['id'])) {
    $response['code'] = 'invalid_request';
    $response['status'] = $api_response_code[ $response['code'] ]['HTTP Response'];
    $response['data'] = $api_response_code[ $response['code'] ]['Message']; 
    // Return Response to browser
    deliver_response($format, $response);   
}

$scrapers = json_decode(file_get_contents("scrapers.json"));

if (!isset($scrapers->$_REQUEST['id']))
    $scrapers->$_REQUEST['id'] = new stdClass();
$scraper = $scrapers->$_REQUEST['id'];

if (isset($_REQUEST['id']))
    $scraper->id = $_REQUEST['id'];

if (isset($_REQUEST['name']))
    $scraper->name = $_REQUEST['name'];
if (isset($_REQUEST['description']))
    $scraper->description = $_REQUEST['description'];
if (isset($_REQUEST['url']))
    $scraper->url = $_REQUEST['url'];
   
    //note: 2015-04-29T15:16:55Z

if (isset($_REQUEST['date']) and (check_time($_REQUEST['date'])))
    $scraper->last_run = $_REQUEST['date'];
else
    $scraper->last_run = date('c');

if (isset($_REQUEST['status']) and (in_array($_REQUEST['status'],['ok','failed'])))
    $scraper->last_status = $_REQUEST['status'];
else
    $scraper->last_status = 'unknown';
if (isset($_REQUEST['message']))
    $scraper->last_message = $_REQUEST['message'];
else
    $scraper->last_message = '';

if (!isset($scraper->statistics))
    $scraper->statistics = new stdClass();

$t = $scraper->last_status;
if (!isset($scraper->statistics->$t))
    $scraper->statistics->$t = 0;
$scraper->statistics->$t++;

if (isset($_REQUEST['state']))
    $scraper->state = $_REQUEST['state'];

$fout = fopen("scrapers.json","w");
fwrite($fout,json_encode($scrapers));
fclose($fout);

$response['code'] = 'success';
$response['status'] = $api_response_code[ $response['code'] ]['HTTP Response'];
$response['data'] = $scraper; 

// --- Step 4: Deliver Response
 
// Return Response to browser

deliver_response($format, $response);


/**
* Helper function
*/
function check_time ($time) {
    if (strtotime($time !== false))
        return true;
    else
        return false;
}
?>
