// Лемматизация-нормализация и фильтрация текста для последующей обработки в word2vec


using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using SolarixGrammarEngineNET;

abstract class Samples
{
 public abstract int TotalCount();
 public abstract void Start();
 public abstract string Next();
 public abstract void SetTokenDelimiter( char c );
}


// одна строка - одно предложение
class Samples1 : Samples
{
 string source_filepath;
 System.IO.StreamReader rdr;

 public Samples1( string _source_filepath )
 {
  source_filepath = _source_filepath;
 }

 public override int TotalCount()
 {
  int n_total_lines = 0;

  using( System.IO.StreamReader rdr = new System.IO.StreamReader( source_filepath ) )
  {
   while( true )
   {
    string sample = rdr.ReadLine();
    if( sample == null )
     break;

    n_total_lines++;
   }
  }

  return n_total_lines;
 }

 public override void Start()
 {
  rdr = new System.IO.StreamReader( source_filepath );
  return;
 }

 public override string Next()
 {
  return rdr.ReadLine();
 }

 public override void SetTokenDelimiter( char c )
 {
  throw new NotImplementedException();
 }
}


// одна строка - один токен
class Samples2 : Samples
{
 string source_filepath;
 string[] filenames;
 char token_delimiter = ' ';

 public Samples2( string _source_filepath )
 {
  source_filepath = _source_filepath;

  if( System.IO.File.Exists( source_filepath ) )
   filenames = new string[1] { source_filepath };
  else
   filenames = System.IO.Directory.GetFiles( source_filepath );
 }

 public override int TotalCount()
 {
  int n_total_lines = 0;

  foreach( string filename in filenames )
  {
   using( System.IO.StreamReader rdr = new System.IO.StreamReader( filename ) )
   {
    while( true )
    {
     string sample = rdr.ReadLine();
     if( sample == null )
      break;

     if( sample.Length == 0 )
      n_total_lines++;
    }
   }
  }

  return n_total_lines;
 }

 int current_filename;
 System.IO.StreamReader rdr;

 public override void Start()
 {
  current_filename = -1;
  rdr = null;
  return;
 }

 System.Text.StringBuilder b = new StringBuilder();
 public override string Next()
 {
  if( rdr == null )
  {
   current_filename++;
   if( current_filename >= filenames.Length )
    return null;

   rdr = new System.IO.StreamReader( filenames[current_filename] );
  }

  b.Length = 0;

  while( true )
  {
   string word = rdr.ReadLine();
   if( word == null )
   {
    rdr.Close();
    rdr = null;
    break;
   }
   else if( word.Length == 0 )
   {
    break;
   }
   else
    b.AppendFormat( "{1}{0}", word, token_delimiter );
  }

  return b.ToString();
 }

 public override void SetTokenDelimiter( char c )
 {
  token_delimiter = c;
 }
}




// ---------------------------------------------------------------------


class Program
{
 static void Main( string[] args )
 {
  string dictionary_path = @"e:\MVoice\lem\bin-windows\dictionary.xml"; // путь к словарной базе
  string samples_path = @"E:\MVoice\lem\Слова\rus\SENT5.plain.txt"; // путь к файлу со списком предложений (одно предложение на одной строке)
  int NSAMPLE = 20000; // сколько предложений максимум обработать
  int START_INDEX = 0; // порядковый номер первого обрабатываемого предложений в исходном файле
  int MAXARGS = 20; // beam size
  bool append_result = false; // если леммы надо добавлять к существующему файлу, а не формировать файл с нуля
  string save_path = null; // путь к файлу, куда будут записаны леммы
  int source_format = 0; // 0 - token per line, 1 - sentence per line
  bool output_lemmas = true; // в результат записывать леммы с приведением к нижнему регистру
  bool output_suffix = false;
  bool output_words = false; // в результат записывать исходные слова с приведением к нижнему регистру
  int suffix_len = 0;
  int min_sentence_length = 0; // фильтр по минимальной длине предложений
  int max_sentence_length = int.MaxValue; // фильтр по максимальной длине предложений
  bool reject_unknown = false; // отбрасывать предложения с несловарными токенами

  List<System.Text.RegularExpressions.Regex> rx_stop = new List<System.Text.RegularExpressions.Regex>();

  for( int i = 0; i < args.Length; ++i )
  {
   if( args[i] == "-dict" )
   {
    ++i;
    dictionary_path = args[i];
   }
   else if( args[i] == "-samples" )
   {
    ++i;
    samples_path = args[i];
   }
   else if( args[i] == "-source_format" )
   {
    ++i;
    source_format = int.Parse( args[i] );
   }
   else if( args[i] == "-append" )
   {
    // Добавлять в конец существующего файла
    append_result = true;
   }
   else if( args[i] == "-result" )
   {
    // Способ обработки токенов:
    // lemma  => лемматизация
    // suffix => усечение до псевдосуффикса длиной -suffix_len
    // raw    => исходные слова
    ++i;
    output_lemmas = false;
    output_suffix = false;
    output_words = false;

    if( args[i] == "suffix" )
    {
     output_suffix = true;
    }
    else if( args[i] == "lemma" )
    {
     output_lemmas = true;
    }
    else if( args[i] == "raw" )
    {
     output_words = true;
    }
    else throw new ApplicationException( string.Format( "Unknown result format: {0}", args[i] ) );
   }
   else if( args[i] == "-save" )
   {
    // Путь к файлу, куда будут записываться результаты обработки
    ++i;
    save_path = args[i];
   }
   else if( args[i] == "-nsample" )
   {
    // кол-во обрабатываемых предложений, начиная с -start_index
    ++i;
    NSAMPLE = int.Parse( args[i] );
   }
   else if( args[i] == "-min_sent_len" )
   {
    // Обрабатывать только предложения, содержащие не менее NNN токенов
    ++i;
    min_sentence_length = int.Parse( args[i] );
   }
   else if( args[i] == "-max_sent_len" )
   {
    // Обрабатывать только предложения, содержащие не более NNN токенов
    ++i;
    max_sentence_length = int.Parse( args[i] );
   }
   else if( args[i] == "-suffix_len" )
   {
    ++i;
    suffix_len = int.Parse( args[i] );
   }
   else if( args[i] == "-start_index" )
   {
    // Начинать обработку с предложения с указанным индексом
    ++i;
    START_INDEX = int.Parse( args[i] );
   }
   else if( args[i] == "-reject_unknown" )
   {
    reject_unknown = true;
   }
   else if( args[i] == "-rx_stop" )
   {
    ++i;
    using( System.IO.StreamReader rdr = new System.IO.StreamReader( args[i] ) )
    {
     while( !rdr.EndOfStream )
     {
      string line = rdr.ReadLine();
      if( line == null )
       break;

      line = line.Trim();
      if( line.Length > 0 )
      {
       rx_stop.Add( new System.Text.RegularExpressions.Regex( line ) );
      }
     }
    }
   }
   else
    throw new ApplicationException( string.Format( "Unknown option {0}", args[i] ) );
  }


  Samples sources = null;
  if( source_format == 1 )
   sources = new Samples1( samples_path );
  else
   sources = new Samples2( samples_path );


  if( output_suffix || output_words )
   sources.SetTokenDelimiter( '|' );

  SolarixGrammarEngineNET.GrammarEngine2 gren = null;
  gren = new SolarixGrammarEngineNET.GrammarEngine2();

  if( output_lemmas )
  {
   gren.Load( dictionary_path, true );
  }

  int counter = -1;
  int n_processed = 1;
  int MAX_COUNT = NSAMPLE;

  int LanguageID = SolarixGrammarEngineNET.GrammarEngineAPI.RUSSIAN_LANGUAGE;
  int Constraints = 120000 | ( MAXARGS << 22 ); // 2 мин и 20 альтернатив

  SolarixGrammarEngineNET.GrammarEngine.MorphologyFlags Flags = SolarixGrammarEngineNET.GrammarEngine.MorphologyFlags.SOL_GREN_MODEL_ONLY |
        SolarixGrammarEngineNET.GrammarEngine.MorphologyFlags.SOL_GREN_MODEL;

  // сколько всего предложений
  Console.WriteLine( "Counting lines in source file {0}...", samples_path );
  int n_total_lines = sources.TotalCount();
  Console.WriteLine( "Total number of lines={0}", n_total_lines.ToString( "N0", new System.Globalization.CultureInfo( "en-US" ) ) );

  System.IO.StreamWriter wrt = new System.IO.StreamWriter( save_path, append_result, new UTF8Encoding( false ) );

  sources.Start();
  while( true )
  {
   string sample = sources.Next();
   if( sample == null )
    break;

   sample = sample.Trim();

   counter++;

   if( counter < START_INDEX )
    continue;

   if( n_processed >= MAX_COUNT )
    break;

   bool contains_insane_chars = false;
   foreach( char c in sample )
    if( c < 32 )
    {
     contains_insane_chars = true;
     break;
    }

   if( contains_insane_chars )
   {
    System.Text.StringBuilder b = new StringBuilder( sample.Length );
    foreach( char c in sample )
     if( c >= 32 )
      b.Append( c );

    sample = b.ToString();
   }

   n_processed++;

   if( sample.Length == 0 )
    continue;


   if( rx_stop.Count > 0 )
   {
    bool reject_this_sample = false;
    foreach( var rx in rx_stop )
     if( rx.Match( sample ).Success )
     {
      reject_this_sample = true;
      break;
     }

    if( reject_this_sample )
     continue;
   }

   if( output_lemmas )
   {
    using( SolarixGrammarEngineNET.AnalysisResults tokens = gren.AnalyzeMorphology( sample, LanguageID, Flags, Constraints ) )
    {
     if( min_sentence_length > 0 || max_sentence_length < int.MaxValue && tokens.Count < min_sentence_length || tokens.Count > max_sentence_length )
      continue;

     for( int i = 1; i < tokens.Count - 1; ++i )
     {
      if( char.IsPunctuation( tokens[i].GetWord()[0] ) )
       continue;

      int id_entry = tokens[i].GetEntryID();
      string lemma = gren.GetEntryName( id_entry );
      if( lemma == "???" || lemma.Equals( "UNKNOWNENTRY", StringComparison.InvariantCultureIgnoreCase ) || lemma.Equals( "number_", StringComparison.InvariantCultureIgnoreCase ) )
       lemma = tokens[i].GetWord();

      lemma = lemma.ToLower();
      wrt.Write( " {0}", lemma );
     }
    }
   }
   else if( output_words )
   {
    string[] tokens = sample.Split( "|".ToCharArray(), StringSplitOptions.RemoveEmptyEntries );

    if( min_sentence_length > 0 || max_sentence_length < int.MaxValue && tokens.Length < min_sentence_length || tokens.Length > max_sentence_length )
     continue;

    foreach( string token in tokens )
    {
     if( token.Length >= 1 && char.IsPunctuation( token[0] ) )
      continue;

     string norma = token.ToLower();
     wrt.Write( " {0}", norma );
    }
   }
   else if( output_suffix )
   {
    string[] tokens = sample.Split( "|".ToCharArray(), StringSplitOptions.RemoveEmptyEntries );

    if( min_sentence_length > 0 || max_sentence_length < int.MaxValue && tokens.Length < min_sentence_length || tokens.Length > max_sentence_length )
     continue;

    foreach( string token in tokens )
    {
     if( token.Length == 0 || ( token.Length == 1 && char.IsPunctuation( token[0] ) ) )
      continue;

     string suffix = token;


     int num;
     if( int.TryParse( token, out num ) )
      suffix = token.Substring( token.Length - 1 );
     else if( token.Length > suffix_len + 1 )
      suffix = "~" + token.Substring( token.Length - suffix_len );

     wrt.Write( " {0}", suffix.ToLower() );
    }
   }

   Console.WriteLine( "[{1}/{2}] {0}", sample, counter, n_total_lines );

   wrt.Flush();
  }

  wrt.Close();

  return;
 }
}
