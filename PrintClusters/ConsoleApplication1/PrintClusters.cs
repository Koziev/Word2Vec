using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

class Program
{
 static void Main( string[] args )
 {
  string corpus_path = args[0];
  string classes_path = args[1];
  string result_path = args[2];

  Dictionary<string, int> word2freq = new Dictionary<string, int>();
  using( System.IO.StreamReader rdr = System.IO.File.OpenText( corpus_path ) )
  {
   int BUF_SIZE = 16384;
   char[] buffer = new char[BUF_SIZE];
   string prev_token_head = null;

   while( rdr.EndOfStream == false )
   {
    int nchar = rdr.ReadBlock( buffer, 0, BUF_SIZE );
    if( nchar < 0 )
     break;

    string[] words = new string( buffer ).Split( ' ' );

    if( !string.IsNullOrEmpty( prev_token_head ) && words.Length > 0 )
     words[0] = prev_token_head + words[0];

    int nword = words.Length;
    if( buffer[BUF_SIZE - 1] != ' ' )
    {
     nword--;
     prev_token_head = words[words.Length - 1];
    }

    for( int i = 0; i < nword; ++i )
    {
     if( words[i].Length > 0 )
     {
      int freq;
      if( word2freq.TryGetValue( words[i], out freq ) )
       word2freq[words[i]] = freq + 1;
      else
       word2freq.Add( words[i], 1 );
     }
    }
   }
  }

  Dictionary<int, List<string>> class2words = new Dictionary<int, List<string>>();
  using( System.IO.StreamReader rdr = new System.IO.StreamReader( classes_path ) )
  {
   while( !rdr.EndOfStream )
   {
    string line = rdr.ReadLine();
    if( line == null )
     break;

    string[] toks = line.Split( ' ' );
    string word = toks[0];
    int class_index = int.Parse( toks[1] );
    List<string> words;
    if( !class2words.TryGetValue( class_index, out words ) )
    {
     words = new List<string>();
     class2words.Add( class_index, words );
    }

    words.Add( word );
   }
  }

  using( System.IO.StreamWriter wrt = new System.IO.StreamWriter( result_path ) )
  {
//   foreach( var p in class2words.OrderBy( z => z.Key ) )
   foreach( var p in class2words.OrderByDescending( z => z.Value.Select( q => word2freq.ContainsKey(q) ? word2freq[q] : 0 ).Sum() ) )
   {
    wrt.Write( "{0}\t", p.Key );
    wrt.Write( "{0}", string.Join( " ", p.Value.Where( z => word2freq.ContainsKey( z ) ).OrderByDescending( z => word2freq[z] ).ToArray() ) );
    wrt.WriteLine( "" );
   }
  }

  return;
 }
}
