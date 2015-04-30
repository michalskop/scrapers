<?php

$scrapersobj = json_decode(file_get_contents("scrapers.json"));
$scrapers = [];
foreach ($scrapersobj as $scraper)
    $scrapers[] = $scraper;
usort($scrapers, 'sort_objects');

?>
<!DOCTYPE html>
<html lang="en">

  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Scrapers">
    <meta name="author" content="Michal Škop">
    <link type="image/x-icon" href="favicon.ico" rel="shortcut icon">
    


    <link href="//cdnjs.cloudflare.com/ajax/libs/bootswatch/3.3.4/slate/bootstrap.css" rel="stylesheet">
    <link href="//netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.min.css" rel="stylesheet">
     
    
      <title>Scrapers</title>
    
  </head>
    <body>
      <!-- header -->
        <header id="top" role="banner">
          <nav class="navbar navbar-default" role="navigation">
            <div class="container">
              <a class="navbar-brand" href="#" id="header-home">Scrapers</a>
            </div>
          </nav>
        </header>
      <!-- /header -->
      <div class="bs-docs-header" id="content">
        <div class="container">
            <table class="table table-striped">
                <tr>
                    <th>Scraper</th>
                    <th>Last Run</th>
                    <th>Statistics</th>
                </tr>
                <?php foreach ($scrapers as $scraper) { ?>
                    <?php if(isset($scraper->state) and ($scraper->state != 'inactive')) { ?>
                        <tr class="
                            <?php if ($scraper->last_status == 'ok') echo('success'); elseif ($scraper->last_status == 'failed') echo('danger'); ?>                 
                        ">
                            <td>
                                <?php if (isset($scraper->url)) echo("<a href='".$scraper->url."'>"); ?>
                                <?php if (isset($scraper->name)) echo($scraper->name); else echo ($scraper->id); ?>
                                <?php if (isset($scraper->description)) echo("<br><small>".$scraper->description."</small>"); ?>
                                <?php if (isset($scraper->url)) echo("</a>"); ?>
                            </td>
                            <td>
                                <?php echo(date("Y-m-d H:i:s",strtotime($scraper->last_run))." ");
                                if ($scraper->last_status == 'ok') echo("<i class='fa fa-clock-o fa-1x'></i> "); elseif ($scraper->last_status == 'failed') { echo("<i class='fa  fa-exclamation-circle fa-1x'></i> "); if (isset($scraper->last_message)) echo($scraper->last_message);} else  echo("<i class='fa fa-question fa-1x'></i> "); ?>
                            </td>
                            <td>
                                <?php 
                                  if (isset($scraper->statistics->ok))
                                    echo("<span class='badge text-success'>".$scraper->statistics->ok."</span>, ");
                                  if (isset($scraper->statistics->failed))
                                    echo("<span class='badge text-danger'>".$scraper->statistics->failed."</span>, ");
                                  if (isset($scraper->statistics->unknown))
                                    echo("<span class='badge text-muted'>".$scraper->statistics->unknown."</span>");
                                    
                                ?>
                                    
                            </td>
                        </tr>
                    <?php } ?>    
                <?php } ?>
            </table>
        </div>
      </div>
    </body>
</html>
  
<?php

function sort_objects($a, $b) {
    if (!isset($a->weight))
        $a->weight = 1000000;
    if (!isset($b->weight))
        $b->weight = 1000000;
	if($a->weight == $b->weight){ return 0 ; }
	return ($a->weight < $b->weight) ? -1 : 1;
}

?>
