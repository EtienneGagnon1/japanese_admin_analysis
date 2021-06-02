library(quanteda)
library(data.table)
library(wordcloud2)
library(dplyr)

get_tfidf_top_words <- function(dfm_row, n = 50){
  
  
  reordered <- order(dfm_row, decreasing = TRUE)

    dfm_row <- dfm_row[reordered]
  top_words <- names(dfm_row)[1:n]
  
  
  return(top_words)
}

path_to_text <- "formatted_data"
text_files <- list.files(path_to_text)


for (text_file in text_files){
  print(text_file)
  
  text_location <- file.path(path_to_text, text_file)
  agency_texts <- data.table::fread(text_location, header = TRUE, encoding = "UTF-8")  
  
  text_dfm <- dfm(agency_texts$text, remove = stopwords("ja", source = "marimo"))
  trimmed_dfm <- dfm_trim(text_dfm, min_docfreq = 0.005, max_docfreq = 0.4, docfreq_type = "prop")
  
  
  
  tf_idf_words <- dfm_tfidf(trimmed_dfm)
  num_docs <- nrow(tf_idf_words)
  
  tf_idf_topwords <- apply(tf_idf_words, MARGIN = 1, get_tfidf_top_words)
  top_words <- apply(tf_idf_topwords, MARGIN = 2, FUN = paste, collapse = " ") 
  
  agency_texts <- mutate(agency_texts, topwords = top_words)
  fwrite(agency_texts, file = text_location)
}

