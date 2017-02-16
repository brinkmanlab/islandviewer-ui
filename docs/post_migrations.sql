ALTER TABLE Analysis CHANGE owner_id owner_id int(11) NOT NULL DEFAULT 0;

DROP TRIGGER IF EXISTS updatestatus;
DELIMITER ;;
CREATE TRIGGER updatestatus BEFORE UPDATE ON Analysis
 FOR EACH ROW BEGIN
    IF NEW.status = 2 THEN
      SET NEW.start_date = NOW();
    ELSEIF NEW.status = 3 OR NEW.status = 4 THEN
      SET NEW.complete_date = NOW();
    END IF;
 END ;;
DELIMITER ;

ALTER TABLE CustomGenome CHANGE owner_id owner_id int(11) NOT NULL DEFAULT 0;

ALTER TABLE CustomGenome CHANGE contigs contigs int(11) NOT NULL DEFAULT 1;

ALTER TABLE CustomGenome CHANGE genome_status genome_status enum('NEW','UNCONFIRMED','MISSINGSEQ','MISSINGCDS','VALID','READY','INVALID') NOT NULL DEFAULT 'NEW';

ALTER TABLE CustomGenome CHANGE submit_date submit_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE Genes CHANGE strand strand tinyint(4) NOT NULL DEFAULT 1;

ALTER TABLE NameCache CHANGE isvalid isvalid tinyint(4) NOT NULL DEFAULT 1;

ALTER TABLE UploadGenome CHANGE email email varchar(254) NOT NULL;

ALTER TABLE Notification CHANGE email email varchar(254) NOT NULL;

ALTER TABLE UploadGenome CHANGE date_uploaded date_uploaded timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE UploadGenome CHANGE cid cid INT(11) NOT NULL DEFAULT 0;

ALTER TABLE GIAnalysisTask CHANGE parameters parameters text;

ALTER TABLE SiteStatus CHANGE status status int(11) NOT NULL DEFAULT '0';

ALTER TABLE virulence CHANGE source source enum('VFDB','ARDB','PAG','CARD','RGI','Victors','PATRIC_VF','BLAST',',') DEFAULT NULL;

ALTER TABLE virulence CHANGE type type enum('resistance','virulence','pathogen-associated') NOT NULL;

ALTER TABLE virulence DROP PRIMARY KEY, ADD PRIMARY KEY (protein_accnum, external_id);

ALTER TABLE virulence_mapped CHANGE source source enum('VFDB','ARDB','PAG','CARD','RGI','Victors','PATRIC_VF','BLAST',',') DEFAULT NULL;

ALTER TABLE virulence_mapped CHANGE type type enum('resistance','virulence','pathogen-associated') NOT NULL;
