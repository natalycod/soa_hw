# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mafia.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='mafia.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0bmafia.proto\"?\n\x14\x43hatReceiversRequest\x12\x14\n\x0csession_name\x18\x01 \x01(\t\x12\x11\n\tuser_name\x18\x02 \x01(\t\";\n\x15\x43hatReceiversResponse\x12\x0f\n\x07in_game\x18\x01 \x01(\x08\x12\x11\n\treceivers\x18\x02 \x03(\t2I\n\x05Mafia\x12@\n\rChatReceivers\x12\x15.ChatReceiversRequest\x1a\x16.ChatReceiversResponse\"\x00\x62\x06proto3'
)




_CHATRECEIVERSREQUEST = _descriptor.Descriptor(
  name='ChatReceiversRequest',
  full_name='ChatReceiversRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='session_name', full_name='ChatReceiversRequest.session_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='user_name', full_name='ChatReceiversRequest.user_name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=15,
  serialized_end=78,
)


_CHATRECEIVERSRESPONSE = _descriptor.Descriptor(
  name='ChatReceiversResponse',
  full_name='ChatReceiversResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='in_game', full_name='ChatReceiversResponse.in_game', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='receivers', full_name='ChatReceiversResponse.receivers', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=80,
  serialized_end=139,
)

DESCRIPTOR.message_types_by_name['ChatReceiversRequest'] = _CHATRECEIVERSREQUEST
DESCRIPTOR.message_types_by_name['ChatReceiversResponse'] = _CHATRECEIVERSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ChatReceiversRequest = _reflection.GeneratedProtocolMessageType('ChatReceiversRequest', (_message.Message,), {
  'DESCRIPTOR' : _CHATRECEIVERSREQUEST,
  '__module__' : 'mafia_pb2'
  # @@protoc_insertion_point(class_scope:ChatReceiversRequest)
  })
_sym_db.RegisterMessage(ChatReceiversRequest)

ChatReceiversResponse = _reflection.GeneratedProtocolMessageType('ChatReceiversResponse', (_message.Message,), {
  'DESCRIPTOR' : _CHATRECEIVERSRESPONSE,
  '__module__' : 'mafia_pb2'
  # @@protoc_insertion_point(class_scope:ChatReceiversResponse)
  })
_sym_db.RegisterMessage(ChatReceiversResponse)



_MAFIA = _descriptor.ServiceDescriptor(
  name='Mafia',
  full_name='Mafia',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=141,
  serialized_end=214,
  methods=[
  _descriptor.MethodDescriptor(
    name='ChatReceivers',
    full_name='Mafia.ChatReceivers',
    index=0,
    containing_service=None,
    input_type=_CHATRECEIVERSREQUEST,
    output_type=_CHATRECEIVERSRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_MAFIA)

DESCRIPTOR.services_by_name['Mafia'] = _MAFIA

# @@protoc_insertion_point(module_scope)
