#!/bin/bash

search_dir='/Users/cwillis/GitHub/RomanCoinData/data_raw/CNG/html/*.htm*'
entries=`ls $search_dir`
for entry in $entries; do
    echo $entry
    # get file name
    # strip .X
    # write to .csv
done


#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Augustus_AR_EA1.htm' > 'Augustus_AR_EA1.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Augustus_AR_EA2.htm' > 'Augustus_AR_EA2.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Augustus_AR_EA3.htm' > 'Augustus_AR_EA3.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Augustus_AR_EA4.htm' > 'Augustus_AR_EA4.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Augustus_AR_PA1.html' > 'Augustus_AR_PA1.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Augustus_AR_PA2.html' > 'Augustus_AR_PA2.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Augustus_AR_PA3.html' > 'Augustus_AR_PA3.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Augustus_AV_EA.htm' > 'Augustus_AV_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Augustus_AV_PA.html' > 'Augustus_AV_PA.csv'

#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Aurelius_AR_EA1.htm' > 'Aurelius_AR_EA1.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Aurelius_AR_EA2.htm' > 'Aurelius_AR_EA2.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Aurelius_AR_PA.html' > 'Aurelius_AR_PA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Aurelius_AV_EA.htm' > 'Aurelius_AV_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Aurelius_AV_PA.html' > 'Aurelius_AV_PA.csv'

#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Aurelius_Caes_AR_EA.htm' > 'Aurelius_Caes_AR_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Aurelius_Caes_AR_PA.html' > 'Aurelius_Caes_AR_PA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Aurelius_Caes_AV_EA.htm' > 'Aurelius_Caes_AV_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Aurelius_Caes_AV_PA.html' > 'Aurelius_Caes_AV_PA.csv'

#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Domitian_AR_EA1.html' > 'Domitian_AR_EA1.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Domitian_AR_EA2.htm' > 'Domitian_AR_EA2.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Domitian_AR_PA.html' > 'Domitian_AR_PA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Domitian_AV_EA.htm' > 'Domitian_AV_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Domitian_AV_PA.html' > 'Domitian_AV_PA.csv'

#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Galba_AR_EA1.htm' > 'Galba_AR_EA1.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Galba_AR_EA2.htm' > 'Galba_AR_EA2.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Galba_AR_PA.htm' > 'Galba_AR_PA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Galba_AV_EA.htm' > 'Galba_AV_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Galba_AV_PA.htm' > 'Galba_AV_PA.csv'

#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Hadrian_AR_EA1.htm' > 'Hadrian_AR_EA1.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Hadrian_AR_EA2.htm' > 'Hadrian_AR_EA2.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Hadrian_AR_EA3.htm' > 'Hadrian_AR_EA3.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Hadrian_AR_EA4.htm' > 'Hadrian_AR_EA4.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Hadrian_AR_EA5.htm' > 'Hadrian_AR_EA5.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Hadrian_AR_PA1.html' > 'Hadrian_AR_PA1.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Hadrian_AR_PA2.html' > 'Hadrian_AR_PA2.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Hadrian_AV_EA.htm' > 'Hadrian_AV_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Hadrian_AV_PA.html' > 'Hadrian_AV_PA.csv'

#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Nero_AR_EA1.htm' > 'Nero_AR_EA1.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Nero_AR_EA2.htm' > 'Nero_AR_EA2.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Nero_AR_PA.html' > 'Nero_AR_PA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Nero_AV_EA.htm' > 'Nero_AV_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Nero_AV_PA.html' > 'Nero_AV_PA.csv'

#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Pius_AR_EA1.html' > 'Pius_AR_EA1.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Pius_AR_EA2.html' > 'Pius_AR_EA2.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Pius_AR_EA3.html' > 'Pius_AR_EA3.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Pius_AR_PA.html' > 'Pius_AR_PA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Pius_AV_EA.html' > 'Pius_AV_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Pius_AV_PA.html' > 'Pius_AV_PA.csv'

#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Tiberius_AR_EA1.htm' > 'Tiberius_AR_EA1.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Tiberius_AR_EA2.htm' > 'Tiberius_AR_EA2.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Tiberius_AR_PA.html' > 'Tiberius_AR_PA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Tiberius_AV_EA.htm' > 'Tiberius_AV_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Tiberius_AV_PA.html' > 'Tiberius_AV_PA.csv'

#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Trajan_AR_EA1.htm' > 'Trajan_AR_EA1.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Trajan_AR_EA2.htm' > 'Trajan_AR_EA2.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Trajan_AR_EA3.htm' > 'Trajan_AR_EA3.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Trajan_AR_PA.html' > 'Trajan_AR_PA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Trajan_AV_EA.htm' > 'Trajan_AV_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Trajan_AV_PA.html' > 'Trajan_AV_PA.csv'

#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Vespasian_AR_EA1.htm' > 'Vespasian_AR_EA1.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Vespasian_AR_EA2.htm' > 'Vespasian_AR_EA2.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Vespasian_AR_EA3.htm' > 'Vespasian_AR_EA3.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Vespasian_AR_EA4.htm' > 'Vespasian_AR_EA4.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Vespasian_AR_PA.html' > 'Vespasian_AR_PA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Vespasian_AV_EA.htm' > 'Vespasian_AV_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Vespasian_AV_PA.html' > 'Vespasian_AV_PA.csv'

#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Otho_AR_EA.htm' > 'Otho_AR_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Otho_AR_PA.htm' > 'Otho_AR_PA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Otho_AV_EA.htm' > 'Otho_AV_EA.csv'
#python3 get_descriptions.py '/Users/cwillis/GitHub/RomanCoinModel/data_raw/CNG/html/Otho_AV_PA.htm' > 'Otho_AV_PA.csv'

# get titus


