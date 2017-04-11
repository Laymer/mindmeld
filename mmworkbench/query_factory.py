# -*- coding: utf-8 -*-
"""This module contains the query factory class."""
from __future__ import unicode_literals
from builtins import object


from . import ser as sys_ent_rec

from .core import Query, TEXT_FORM_RAW, TEXT_FORM_PROCESSED, TEXT_FORM_NORMALIZED
from .tokenizer import Tokenizer


class QueryFactory(object):
    """An object which encapsulates the components required to create a Query object.

    Attributes:
        preprocessor (Preprocessor): the object responsible for processing raw text
        tokenizer (Tokenizer): the object responsible for normalizing and tokenizing processed
            text
    """
    def __init__(self, tokenizer, preprocessor=None):
        self.tokenizer = tokenizer
        self.preprocessor = preprocessor

    def create_query(self, text):
        """Creates a query with the given text

        Args:
            text (str): Text to create a query object for

        Returns:
            Query: A newly constructed query
        """
        raw_text = text

        char_maps = {}

        # create raw, processed maps
        if self.preprocessor:
            processed_text = self.preprocessor.process(raw_text)
            maps = self.preprocessor.get_char_index_map(raw_text, processed_text)
            forward, backward = maps
            char_maps[(TEXT_FORM_RAW, TEXT_FORM_PROCESSED)] = forward
            char_maps[(TEXT_FORM_PROCESSED, TEXT_FORM_RAW)] = backward
        else:
            processed_text = raw_text

        normalized_tokens = self.tokenizer.tokenize(processed_text, False)
        normalized_text = ' '.join([t['entity'] for t in normalized_tokens])

        # create normalized maps
        maps = self.tokenizer.get_char_index_map(processed_text, normalized_text)
        forward, backward = maps

        char_maps[(TEXT_FORM_PROCESSED, TEXT_FORM_NORMALIZED)] = forward
        char_maps[(TEXT_FORM_NORMALIZED, TEXT_FORM_PROCESSED)] = backward

        query = Query(raw_text, processed_text, normalized_tokens, char_maps)
        query.system_entity_candidates = sys_ent_rec.get_candidates(query)
        return query

    def normalize(self, text):
        """Normalizes the given text

        Args:
            text (str): Text to process

        Returns:
            str: Normalized text
        """
        return self.tokenizer.normalize(text)

    def __repr__(self):
        return "<{} id: {!r}>".format(self.__class__.__name__, id(self))

    @staticmethod
    def create_query_factory(app_path, tokenizer=None, preprocessor=None):
        """Creates a query factory for the app

        Args:
            app_path (str): The path to the directory containing the app's data
            tokenizer (Tokenizer, optional): The app's tokenizer. One will be
                created if none is provided
            preprocessor (Processor, optional): The app's preprocessor.

        Returns:
            QueryFactory: Description
        """
        tokenizer = tokenizer or Tokenizer.create_tokenizer(app_path)
        return QueryFactory(tokenizer, preprocessor)