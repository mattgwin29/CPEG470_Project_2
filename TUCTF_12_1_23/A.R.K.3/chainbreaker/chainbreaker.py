#!/usr/bin/python

# Author : n0fate
# E-Mail rapfer@gmail.com, n0fate@n0fate.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

import argparse
import os
from sys import exit
import struct
from binascii import unhexlify
import datetime
from hexdump import hexdump 

from pbkdf2 import pbkdf2

from pyDes import triple_des, CBC
from ctypes import *
from Schema import *

ATOM_SIZE = 4
SIZEOFKEYCHAINTIME = 16

KEYCHAIN_SIGNATURE = "kych"

DBBLOB_SIGNATURE = unhexlify('fade0711')

BLOCKSIZE = 8
KEYLEN = 24

class _APPL_DB_HEADER(BigEndianStructure):
    _fields_ = [
        ("Signature", c_char*4),
        ("Version", c_int),
        ("HeaderSize", c_int),
        ("SchemaOffset", c_int),
        ("AuthOffset", c_int)
    ]

class _APPL_DB_SCHEMA(BigEndianStructure):
    _fields_ = [
        ("SchemaSize", c_int),
        ("TableCount", c_int)
    ]

class _KEY_BLOB_REC_HEADER(BigEndianStructure):
    _fields_ = [
        ("RecordSize", c_uint),
        ("RecordCount", c_uint),
        ("Dummy", c_char*0x7C),
    ]

class _KEY_BLOB_RECORD(BigEndianStructure):
    _fields_ = [
        ("Signature", c_uint),
        ("Version", c_uint),
        ("CipherOffset", c_uint),
        ("TotalLength", c_uint)
    ]

class _GENERIC_PW_HEADER(BigEndianStructure):
    _fields_ = [
        ("RecordSize", c_uint),
        ("RecordNumber", c_uint),
        ("Unknown2", c_uint),
        ("Unknown3", c_uint),
        ("SSGPArea", c_uint),
        ("Unknown5", c_uint),
        ("CreationDate", c_uint),
        ("ModDate", c_uint),
        ("Description", c_uint),
        ("Comment", c_uint),
        ("Creator", c_uint),
        ("Type", c_uint),
        ("ScriptCode", c_uint),
        ("PrintName", c_uint),
        ("Alias", c_uint),
        ("Invisible", c_uint),
        ("Negative", c_uint),
        ("CustomIcon", c_uint),
        ("Protected", c_uint),
        ("Account", c_uint),
        ("Service", c_uint),
        ("Generic", c_uint)
    ]

class _APPLE_SHARE_HEADER(BigEndianStructure):
    _fields_ = [
        ("RecordSize", c_uint),
        ("RecordNumber", c_uint),
        ("Unknown2", c_uint),
        ("Unknown3", c_uint),
        ("SSGPArea", c_uint),
        ("Unknown5", c_uint),
        ("CreationDate", c_uint),
        ("ModDate", c_uint),
        ("Description", c_uint),
        ("Comment", c_uint),
        ("Creator", c_uint),
        ("Type", c_uint),
        ("ScriptCode", c_uint),
        ("PrintName", c_uint),
        ("Alias", c_uint),
        ("Invisible", c_uint),
        ("Negative", c_uint),
        ("CustomIcon", c_uint),
        ("Protected", c_uint),
        ("Account", c_uint),
        ("Volume", c_uint),
        ("Server", c_uint),
        ("Protocol", c_uint),
        ("AuthType", c_uint),
        ("Address", c_uint),
        ("Signature", c_uint)
    ]

class _INTERNET_PW_HEADER(BigEndianStructure):
    _fields_ = [
        ("RecordSize", c_uint),
        ("RecordNumber", c_uint),
        ("Unknown2", c_uint),
        ("Unknown3", c_uint),
        ("SSGPArea", c_uint),
        ("Unknown5", c_uint),
        ("CreationDate", c_uint),
        ("ModDate", c_uint),
        ("Description", c_uint),
        ("Comment", c_uint),
        ("Creator", c_uint),
        ("Type", c_uint),
        ("ScriptCode", c_uint),
        ("PrintName", c_uint),
        ("Alias", c_uint),
        ("Invisible", c_uint),
        ("Negative", c_uint),
        ("CustomIcon", c_uint),
        ("Protected", c_uint),
        ("Account", c_uint),
        ("SecurityDomain", c_uint),
        ("Server", c_uint),
        ("Protocol", c_uint),
        ("AuthType", c_uint),
        ("Port", c_uint),
        ("Path", c_uint)
    ]

class _X509_CERT_HEADER(BigEndianStructure):
    _fields_ = [
        ("RecordSize", c_uint),
        ("RecordNumber", c_uint),
        ("Unknown1", c_uint),
        ("Unknown2", c_uint),
        ("CertSize", c_uint),
        ("Unknown3", c_uint),
        ("CertType", c_uint),
        ("CertEncoding", c_uint),
        ("PrintName", c_uint),
        ("Alias", c_uint),
        ("Subject", c_uint),
        ("Issuer", c_uint),
        ("SerialNumber", c_uint),
        ("SubjectKeyIdentifier", c_uint),
        ("PublicKeyHash", c_uint)
    ]

# http://www.opensource.apple.com/source/Security/Security-55179.1/include/security_cdsa_utilities/KeySchema.h
# http://www.opensource.apple.com/source/libsecurity_keychain/libsecurity_keychain-36940/lib/SecKey.h
class _SECKEY_HEADER(BigEndianStructure):
    _fields_ = [
        ("RecordSize", c_uint),
        ("RecordNumber", c_uint),
        ("Unknown1", c_uint),
        ("Unknown2", c_uint),
        ("BlobSize", c_uint),
        ("Unknown3", c_uint),
        ("KeyClass", c_uint),
        ("PrintName", c_uint),
        ("Alias", c_uint),
        ("Permanent", c_uint),
        ("Private", c_uint),
        ("Modifiable", c_uint),
        ("Label", c_uint),
        ("ApplicationTag", c_uint),
        ("KeyCreator", c_uint),
        ("KeyType", c_uint),
        ("KeySizeInBits", c_uint),
        ("EffectiveKeySize", c_uint),
        ("StartDate", c_uint),
        ("EndDate", c_uint),
        ("Sensitive", c_uint),
        ("AlwaysSensitive", c_uint),
        ("Extractable", c_uint),
        ("NeverExtractable", c_uint),
        ("Encrypt", c_uint),
        ("Decrypt", c_uint),
        ("Derive", c_uint),
        ("Sign", c_uint),
        ("Verify", c_uint),
        ("SignRecover", c_uint),
        ("VerifyRecover", c_uint),
        ("Wrap", c_uint),
        ("Wrap", c_uint)
    ]

class _TABLE_HEADER(BigEndianStructure):
    _fields_ = [
        ("TableSize", c_uint),
        ("TableId", c_uint),
        ("RecordCount", c_uint),
        ("Records", c_uint),
        ("IndexesOffset", c_uint),
        ("FreeListHead", c_uint),
        ("RecordNumbersCount", c_uint),
        #("RecordNumbers", c_uint)
    ]

class _SCHEMA_INFO_RECORD(BigEndianStructure):
    _fields_ = [
        ("RecordSize", c_uint),
        ("RecordNumber", c_uint),
        ("Unknown2", c_uint),
        ("Unknown3", c_uint),
        ("Unknown4", c_uint),
        ("Unknown5", c_uint),
        ("Unknown6", c_uint),
        ("RecordType", c_uint),
        ("DataSize", c_uint),
        ("Data", c_uint)
    ]

class _ENCRYPTED_BLOB_METADATA(BigEndianStructure):
    _fields_ = [
        ("MagicNumber", c_uint),
        ("Unknown", c_uint),
        ("StartOffset", c_uint),
        ("EndOffset", c_uint)
    ]

def _memcpy(buf, fmt):
    return cast(c_char_p(buf), POINTER(fmt)).contents


class KeyChain():
    def __init__(self, filepath):
        self.filepath = filepath
        self.fbuf = ''

    def open(self):
        try:
            fhandle = open(self.filepath, 'rb')
        except:
            return False
        self.fbuf = fhandle.read()
        if len(self.fbuf):
            fhandle.close()
            return True
        return False

    def checkValidKeychain(self):
        if self.fbuf[0:4] != KEYCHAIN_SIGNATURE:
            return False
        return True

    ## get apple DB Header
    def getHeader(self):
        header = _memcpy(self.fbuf[:sizeof(_APPL_DB_HEADER)], _APPL_DB_HEADER)

        return header

    def getSchemaInfo(self, offset):
        table_list = []
        #schema_info = struct.unpack(APPL_DB_SCHEMA, self.fbuf[offset:offset + APPL_DB_SCHEMA_SIZE])
        _schemainfo = _memcpy(self.fbuf[offset:offset+sizeof(_APPL_DB_SCHEMA)], _APPL_DB_SCHEMA)
        for i in xrange(_schemainfo.TableCount):
            BASE_ADDR = sizeof(_APPL_DB_HEADER) + sizeof(_APPL_DB_SCHEMA)
            table_list.append(
                struct.unpack('>I', self.fbuf[BASE_ADDR + (ATOM_SIZE * i):BASE_ADDR + (ATOM_SIZE * i) + ATOM_SIZE])[0])

        return _schemainfo, table_list

    def getTable(self, offset):
        record_list = []
        BASE_ADDR = sizeof(_APPL_DB_HEADER) + offset

        TableMetaData = _memcpy(self.fbuf[BASE_ADDR:BASE_ADDR+sizeof(_TABLE_HEADER)], _TABLE_HEADER)

        RECORD_OFFSET_BASE = BASE_ADDR + sizeof(_TABLE_HEADER)

        record_count = 0
        offset = 0
        while TableMetaData.RecordCount != record_count:
            RecordOffset = struct.unpack('>I', self.fbuf[
                                                RECORD_OFFSET_BASE + (ATOM_SIZE * offset):RECORD_OFFSET_BASE + (
                                                    ATOM_SIZE * offset) + ATOM_SIZE])[0]
            # if len(record_list) >= 1:
            #     if record_list[len(record_list)-1] >= RecordOffset:
            #         continue
            if (RecordOffset != 0x00) and (RecordOffset%4 == 0):
                record_list.append(RecordOffset)
                #print ' [-] Record Offset: 0x%.8x'%RecordOffset
                record_count += 1
            offset +=1

        return TableMetaData, record_list

    def getTablenametoList(self, recordList, tableList):
        TableDic = {}
        for count in xrange(len(recordList)):
            tableMeta, GenericList = self.getTable(tableList[count])
            TableDic[tableMeta.TableId] = count    # extract valid table list

        return len(recordList), TableDic

    def getSchemaInfoRecord(self, base_addr, offset):

        record_meta = []
        record = []

        BASE_ADDR = sizeof(_APPL_DB_HEADER) + base_addr + offset

        #print BASE_ADDR

        RecordMetadata = _memcpy(self.fbuf[BASE_ADDR:BASE_ADDR+sizeof(_SCHEMA_INFO_RECORD)], _SCHEMA_INFO_RECORD)

        data = self.fbuf[BASE_ADDR + 40:BASE_ADDR + 40 + RecordMetadata.DataSize]

        for record_element in RecordMetadata:
            record.append(record_element)

        record.append(data)

        return record

    def getKeyblobRecord(self, base_addr, offset):

        BASE_ADDR = sizeof(_APPL_DB_HEADER) + base_addr + offset

        KeyBlobRecHeader = _memcpy(self.fbuf[BASE_ADDR:BASE_ADDR+sizeof(_KEY_BLOB_REC_HEADER)], _KEY_BLOB_REC_HEADER)


        # record_meta[0] => record size
        record = self.fbuf[BASE_ADDR + sizeof(_KEY_BLOB_REC_HEADER):BASE_ADDR + KeyBlobRecHeader.RecordSize]  # password data area

        KeyBlobRecord = _memcpy(record[:sizeof(_KEY_BLOB_RECORD)], _KEY_BLOB_RECORD)

        if SECURE_STORAGE_GROUP != str(record[KeyBlobRecord.TotalLength + 8:KeyBlobRecord.TotalLength + 8 + 4]):
            #print 'not ssgp %s'%str(record[KeyBlobRecord.TotalLength + 8:KeyBlobRecord.TotalLength + 8 + 4])
            #exit()
            return '', '', '', 1

        CipherLen = KeyBlobRecord.TotalLength - KeyBlobRecord.CipherOffset
        if CipherLen % BLOCKSIZE != 0:
            print "Bad ciphertext len"

        iv = record[16:24]

        ciphertext = record[KeyBlobRecord.CipherOffset:KeyBlobRecord.TotalLength]

        # match data, keyblob_ciphertext, Initial Vector, success
        return record[KeyBlobRecord.TotalLength + 8:KeyBlobRecord.TotalLength + 8 + 20], ciphertext, iv, 0


    def getGenericPWRecord(self, base_addr, offset):
        record = []

        BASE_ADDR = sizeof(_APPL_DB_HEADER) + base_addr + offset

        RecordMeta = _memcpy(self.fbuf[BASE_ADDR:BASE_ADDR+sizeof(_GENERIC_PW_HEADER)], _GENERIC_PW_HEADER)

        Buffer = self.fbuf[BASE_ADDR + sizeof(_GENERIC_PW_HEADER):BASE_ADDR + RecordMeta.RecordSize]  # record_meta[0] => record size

        if RecordMeta.SSGPArea != 0:
            record.append(Buffer[:RecordMeta.SSGPArea])
        else:
            record.append('')
        
        record.append(self.getKeychainTime(BASE_ADDR, RecordMeta.CreationDate & 0xFFFFFFFE))
        record.append(self.getKeychainTime(BASE_ADDR, RecordMeta.ModDate & 0xFFFFFFFE))

        record.append(self.getLV(BASE_ADDR, RecordMeta.Description & 0xFFFFFFFE))

        record.append(self.getFourCharCode(BASE_ADDR, RecordMeta.Creator & 0xFFFFFFFE))
        record.append(self.getFourCharCode(BASE_ADDR, RecordMeta.Type & 0xFFFFFFFE))

        record.append(self.getLV(BASE_ADDR, RecordMeta.PrintName & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Alias & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Account & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Service & 0xFFFFFFFE))

        return record

    def getInternetPWRecord(self, base_addr, offset):
        record = []

        BASE_ADDR = sizeof(_APPL_DB_HEADER) + base_addr + offset

        RecordMeta = _memcpy(self.fbuf[BASE_ADDR:BASE_ADDR+sizeof(_INTERNET_PW_HEADER)], _INTERNET_PW_HEADER)

        Buffer = self.fbuf[BASE_ADDR + sizeof(_INTERNET_PW_HEADER):BASE_ADDR + RecordMeta.RecordSize]

        if RecordMeta.SSGPArea != 0:
            record.append(Buffer[:RecordMeta.SSGPArea])
        else:
            record.append('')

        record.append(self.getKeychainTime(BASE_ADDR, RecordMeta.CreationDate & 0xFFFFFFFE))
        record.append(self.getKeychainTime(BASE_ADDR, RecordMeta.ModDate & 0xFFFFFFFE))

        record.append(self.getLV(BASE_ADDR, RecordMeta.Description & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Comment & 0xFFFFFFFE))

        record.append(self.getFourCharCode(BASE_ADDR, RecordMeta.Creator & 0xFFFFFFFE))
        record.append(self.getFourCharCode(BASE_ADDR, RecordMeta.Type & 0xFFFFFFFE))

        record.append(self.getLV(BASE_ADDR, RecordMeta.PrintName & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Alias & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Protected & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Account & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.SecurityDomain & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Server & 0xFFFFFFFE))

        record.append(self.getFourCharCode(BASE_ADDR, RecordMeta.Protocol & 0xFFFFFFFE))

        record.append(self.getLV(BASE_ADDR, RecordMeta.AuthType & 0xFFFFFFFE))

        record.append(self.getInt(BASE_ADDR, RecordMeta.Port & 0xFFFFFFFE))

        record.append(self.getLV(BASE_ADDR, RecordMeta.Path & 0xFFFFFFFE))        

        return record

    def getx509Record(self, base_addr, offset):
        record = []

        BASE_ADDR = sizeof(_APPL_DB_HEADER) + base_addr + offset

        RecordMeta = _memcpy(self.fbuf[BASE_ADDR:BASE_ADDR+sizeof(_X509_CERT_HEADER)], _X509_CERT_HEADER)

        x509Certificate = self.fbuf[BASE_ADDR + sizeof(_X509_CERT_HEADER):BASE_ADDR + sizeof(_X509_CERT_HEADER) + RecordMeta.CertSize]

        record.append(self.getInt(BASE_ADDR, RecordMeta.CertType & 0xFFFFFFFE))     # Cert Type
        record.append(self.getInt(BASE_ADDR, RecordMeta.CertEncoding & 0xFFFFFFFE))     # Cert Encoding

        record.append(self.getLV(BASE_ADDR, RecordMeta.PrintName & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Alias & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Subject & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Issuer & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.SerialNumber & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.SubjectKeyIdentifier & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.PublicKeyHash & 0xFFFFFFFE))

        record.append(x509Certificate)
        return record

    def getKeyRecord(self, base_addr, offset):  ## PUBLIC and PRIVATE KEY
        record = []

        BASE_ADDR = sizeof(_APPL_DB_HEADER) + base_addr + offset

        RecordMeta = _memcpy(self.fbuf[BASE_ADDR:BASE_ADDR+sizeof(_SECKEY_HEADER)], _SECKEY_HEADER)

        KeyBlob = self.fbuf[BASE_ADDR + sizeof(_SECKEY_HEADER):BASE_ADDR + sizeof(_SECKEY_HEADER) + RecordMeta.BlobSize]

        record.append(self.getLV(BASE_ADDR, RecordMeta.PrintName & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Label & 0xFFFFFFFE))
        record.append(self.getInt(BASE_ADDR, RecordMeta.KeyClass & 0xFFFFFFFE))
        record.append(self.getInt(BASE_ADDR, RecordMeta.Private & 0xFFFFFFFE))
        record.append(self.getInt(BASE_ADDR, RecordMeta.KeyType & 0xFFFFFFFE))
        record.append(self.getInt(BASE_ADDR, RecordMeta.KeySizeInBits & 0xFFFFFFFE))
        record.append(self.getInt(BASE_ADDR, RecordMeta.EffectiveKeySize & 0xFFFFFFFE))
        record.append(self.getInt(BASE_ADDR, RecordMeta.Extractable & 0xFFFFFFFE))
        record.append(str(self.getLV(BASE_ADDR, RecordMeta.KeyCreator & 0xFFFFFFFE)).split('\x00')[0])

        IV, Key = self.getEncryptedDatainBlob(KeyBlob)
        record.append(IV)
        record.append(Key)

        return record

    def getEncryptedDatainBlob(self, BlobBuf):
        magicNumber = 0xFADE0711

        IVSize = 8

        EncryptedBlobMeta = _memcpy(BlobBuf[:sizeof(_ENCRYPTED_BLOB_METADATA)], _ENCRYPTED_BLOB_METADATA)

        if EncryptedBlobMeta.MagicNumber != magicNumber:
            return '', ''

        KeyData = BlobBuf[EncryptedBlobMeta.StartOffset:EncryptedBlobMeta.EndOffset]
        IV = BlobBuf[sizeof(_ENCRYPTED_BLOB_METADATA):sizeof(_ENCRYPTED_BLOB_METADATA)+IVSize]
        return IV, KeyData    # IV, Encrypted Data

    def getKeychainTime(self, BASE_ADDR, pCol):
        if pCol <= 0:
            return ''
        else:
            data = str(struct.unpack('>16s', self.fbuf[BASE_ADDR + pCol:BASE_ADDR + pCol + struct.calcsize('>16s')])[0])
            return datetime.datetime.strptime(data.strip('\x00'), '%Y%m%d%H%M%SZ')

    def getInt(self, BASE_ADDR, pCol):
        if pCol <= 0:
            return 0
        else:
            return struct.unpack('>I', self.fbuf[BASE_ADDR + pCol:BASE_ADDR + pCol + 4])[0]

    def getFourCharCode(self, BASE_ADDR, pCol):
        if pCol <= 0:
            return ''
        else:
            return struct.unpack('>4s', self.fbuf[BASE_ADDR + pCol:BASE_ADDR + pCol + 4])[0]

    def getLV(self, BASE_ADDR, pCol):
        if pCol <= 0:
            return ''

        str_length = struct.unpack('>I', self.fbuf[BASE_ADDR + pCol:BASE_ADDR + pCol + 4])[0]
        # 4byte arrangement
        if (str_length % 4) == 0:
            real_str_len = (str_length / 4) * 4
        else:
            real_str_len = ((str_length / 4) + 1) * 4
        unpack_value = '>' + str(real_str_len) + 's'
        try:
            data = struct.unpack(unpack_value, self.fbuf[BASE_ADDR + pCol + 4:BASE_ADDR + pCol + 4 + real_str_len])[0]
        except struct.error:
            print 'Length is too long : %d'%real_str_len
            return ''
        return data


    def getAppleshareRecord(self, base_addr, offset):
        record = []

        BASE_ADDR = sizeof(_APPL_DB_HEADER) + base_addr + offset

        RecordMeta = _memcpy(self.fbuf[BASE_ADDR:BASE_ADDR+sizeof(_INTERNET_PW_HEADER)], _INTERNET_PW_HEADER)

        Buffer = self.fbuf[BASE_ADDR + sizeof(_INTERNET_PW_HEADER):BASE_ADDR + RecordMeta.RecordSize]

        if RecordMeta.SSGPArea != 0:
            record.append(Buffer[:RecordMeta.SSGPArea])
        else:
            record.append('')

        record.append(self.getKeychainTime(BASE_ADDR, RecordMeta.CreationDate & 0xFFFFFFFE))
        record.append(self.getKeychainTime(BASE_ADDR, RecordMeta.ModDate & 0xFFFFFFFE))

        record.append(self.getLV(BASE_ADDR, RecordMeta.Description & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Comment & 0xFFFFFFFE))

        record.append(self.getFourCharCode(BASE_ADDR, RecordMeta.Creator & 0xFFFFFFFE))
        record.append(self.getFourCharCode(BASE_ADDR, RecordMeta.Type & 0xFFFFFFFE))

        record.append(self.getLV(BASE_ADDR, RecordMeta.PrintName & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Alias & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Protected & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Account & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Volume & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Server & 0xFFFFFFFE))

        record.append(self.getFourCharCode(BASE_ADDR, RecordMeta.Protocol & 0xFFFFFFFE))

        record.append(self.getLV(BASE_ADDR, RecordMeta.Address & 0xFFFFFFFE))
        record.append(self.getLV(BASE_ADDR, RecordMeta.Signature & 0xFFFFFFFE))

        return record

    ## decrypted dbblob area
    ## Documents : http://www.opensource.apple.com/source/securityd/securityd-55137.1/doc/BLOBFORMAT
    ## http://www.opensource.apple.com/source/libsecurity_keychain/libsecurity_keychain-36620/lib/StorageManager.cpp
    def DBBlobDecryption(self, securestoragegroup, dbkey):
        iv = securestoragegroup[20:28]

        plain = kcdecrypt(dbkey, iv, securestoragegroup[28:])

        return plain

    # Documents : http://www.opensource.apple.com/source/securityd/securityd-55137.1/doc/BLOBFORMAT
    # source : http://www.opensource.apple.com/source/libsecurity_cdsa_client/libsecurity_cdsa_client-36213/lib/securestorage.cpp
    # magicCmsIV : http://www.opensource.apple.com/source/Security/Security-28/AppleCSP/AppleCSP/wrapKeyCms.cpp
    def KeyblobDecryption(self, encryptedblob, iv, dbkey):

        magicCmsIV = unhexlify('4adda22c79e82105')
        plain = kcdecrypt(dbkey, magicCmsIV, encryptedblob)

        if plain.__len__() == 0:
            return ''

        # now we handle the unwrapping. we need to take the first 32 bytes,
        # and reverse them.
        revplain = ''
        for i in range(32):
            revplain += plain[31 - i]

        # now the real key gets found. */
        plain = kcdecrypt(dbkey, iv, revplain)

        keyblob = plain[4:]

        if len(keyblob) != KEYLEN:
            #raise "Bad decrypted keylen!"
            return ''

        return keyblob

    # test code
    #http://opensource.apple.com/source/libsecurity_keychain/libsecurity_keychain-55044/lib/KeyItem.cpp
    def PrivateKeyDecryption(self, encryptedblob, iv, dbkey):
        magicCmsIV = unhexlify('4adda22c79e82105')
        plain = kcdecrypt(dbkey, magicCmsIV, encryptedblob)

        if plain.__len__() == 0:
            return ''

        # now we handle the unwrapping. we need to take the first 32 bytes,
        # and reverse them.
        revplain = ''
        for i in range(len(plain)):
            revplain += plain[len(plain)-1 - i]

        # now the real key gets found. */
        plain = kcdecrypt(dbkey, iv, revplain)

        #hexdump(plain)
        Keyname = plain[:12]    # Copied Buffer when user click on right and copy a key on Keychain Access
        keyblob = plain[12:]

        return Keyname, keyblob

    ## Documents : http://www.opensource.apple.com/source/securityd/securityd-55137.1/doc/BLOBFORMAT
    def generateMasterKey(self, pw, symmetrickey_offset):

        base_addr = sizeof(_APPL_DB_HEADER) + symmetrickey_offset + 0x38  # header

        # salt
        SALTLEN = 20
        salt = self.fbuf[base_addr + 44:base_addr + 44 + SALTLEN]

        masterkey = pbkdf2(pw, salt, 1000, KEYLEN)
        return masterkey

    ## find DBBlob and extract Wrapping key
    def findWrappingKey(self, master, symmetrickey_offset):

        base_addr = sizeof(_APPL_DB_HEADER) + symmetrickey_offset + 0x38

        # startCryptoBlob
        cipher_text_offset = struct.unpack('>I', self.fbuf[base_addr + 8:base_addr + 8 + ATOM_SIZE])[0]

        # totalength
        totallength = struct.unpack('>I', self.fbuf[base_addr + 12:base_addr + 12 + ATOM_SIZE])[0]

        # IV
        IVLEN = 8
        iv = self.fbuf[base_addr + 64:base_addr + 64 + IVLEN]

        # get cipher text area
        ciphertext = self.fbuf[base_addr + cipher_text_offset:base_addr + totallength]

        # decrypt the key
        plain = kcdecrypt(master, iv, ciphertext)

        if plain.__len__() == 0:
            return ''

        dbkey = plain[0:KEYLEN]

        # return encrypted wrapping key
        return dbkey


# SOURCE : extractkeychain.py
def kcdecrypt(key, iv, data):
    if len(data) == 0:
        #print>>stderr, "FileSize is 0"
        return data

    if len(data) % BLOCKSIZE != 0:
        return data

    cipher = triple_des(key, CBC, iv)
    # the line below is for pycrypto instead
    #cipher = DES3.new( key, DES3.MODE_CBC, iv )

    plain = cipher.decrypt(data)

    # now check padding
    pad = ord(plain[-1])
    if pad > 8:
        #print>> stderr, "Bad padding byte. You probably have a wrong password"
        return ''

    for z in plain[-pad:]:
        if ord(z) != pad:
            #print>> stderr, "Bad padding. You probably have a wrong password"
            return ''

    plain = plain[:-pad]

    return plain


def main():

    parser = argparse.ArgumentParser(description='Tool for OS X Keychain Analysis by @n0fate')
    parser.add_argument('-f', '--file', nargs=1, help='Keychain file(*.keychain)', required=True)
    #parser.add_argument('-x', '--exportfile', nargs=1, help='Export a filename (SQLite, optional)', required=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-k', '--key', nargs=1, help='Masterkey candidate', required=False)
    group.add_argument('-p', '--password', nargs=1, help='User Password', required=False)
    args = parser.parse_args()

    if os.path.exists(args.file[0]) is False:
        print '[!] ERROR: Keychain is not exists'
        parser.print_help()
        exit()

    keychain = KeyChain(args.file[0])
    
    if keychain.open() is False:
        print '[!] ERROR: %s Open Failed'%args.file[0]
        parser.print_help()
        exit()

    KeychainHeader = keychain.getHeader()

    if KeychainHeader.Signature != KEYCHAIN_SIGNATURE:
        print '[!] ERROR: Invalid Keychain Format'
        parser.print_help()
        exit()

    SchemaInfo, TableList = keychain.getSchemaInfo(KeychainHeader.SchemaOffset)

    TableMetadata, RecordList = keychain.getTable(TableList[0])

    tableCount, tableEnum = keychain.getTablenametoList(RecordList, TableList)

    # generate database key
    if args.password is not None:
        masterkey = keychain.generateMasterKey(args.password[0], TableList[tableEnum[CSSM_DL_DB_RECORD_METADATA]])
        dbkey = keychain.findWrappingKey(masterkey, TableList[tableEnum[CSSM_DL_DB_RECORD_METADATA]])

    elif args.key is not None:
        dbkey = keychain.findWrappingKey(unhexlify(args.key[0]), TableList[tableEnum[CSSM_DL_DB_RECORD_METADATA]])

    else:
        print '[!] ERROR: password or master key candidate'
        exit()

    # DEBUG
    print ' [-] DB Key'
    hexdump(dbkey)

    key_list = {}  # keyblob list

    # get symmetric key blob
    print '[+] Symmetric Key Table: 0x%.8x' % (sizeof(_APPL_DB_HEADER) + TableList[tableEnum[CSSM_DL_DB_RECORD_SYMMETRIC_KEY]])
    TableMetadata, symmetrickey_list = keychain.getTable(TableList[tableEnum[CSSM_DL_DB_RECORD_SYMMETRIC_KEY]])

    for symmetrickey_record in symmetrickey_list:
        keyblob, ciphertext, iv, return_value = keychain.getKeyblobRecord(TableList[tableEnum[CSSM_DL_DB_RECORD_SYMMETRIC_KEY]],
                                                                            symmetrickey_record)
        if return_value == 0:
            passwd = keychain.KeyblobDecryption(ciphertext, iv, dbkey)
            if passwd != '':
                key_list[keyblob] = passwd

    try:
        TableMetadata, genericpw_list = keychain.getTable(TableList[tableEnum[CSSM_DL_DB_RECORD_GENERIC_PASSWORD]])

        for genericpw in genericpw_list:
            record = keychain.getGenericPWRecord(TableList[tableEnum[CSSM_DL_DB_RECORD_GENERIC_PASSWORD]], genericpw)
            print '[+] Generic Password Record'
            try:
                real_key = key_list[record[0][0:20]]
                passwd = keychain.DBBlobDecryption(record[0], real_key)
            except KeyError:
                passwd = ''
            print ' [-] Create DateTime: %s' % record[1]  # 16byte string
            print ' [-] Last Modified DateTime: %s' % record[2]  # 16byte string
            print ' [-] Description : %s' % record[3]
            print ' [-] Creator : %s' % record[4]
            print ' [-] Type : %s' % record[5]
            print ' [-] PrintName : %s' % record[6]
            print ' [-] Alias : %s' % record[7]
            print ' [-] Account : %s' % record[8]
            print ' [-] Service : %s' % record[9]
            print ' [-] Password'
            hexdump(passwd)
            print ''

    except KeyError:
        print '[!] Generic Password Table is not available'
        pass

    try:
        TableMetadata, internetpw_list = keychain.getTable(TableList[tableEnum[CSSM_DL_DB_RECORD_INTERNET_PASSWORD]])

        for internetpw in internetpw_list:
            record = keychain.getInternetPWRecord(TableList[tableEnum[CSSM_DL_DB_RECORD_INTERNET_PASSWORD]], internetpw)
            print '[+] Internet Record'
            try:
                real_key = key_list[record[0][0:20]]
                passwd = keychain.DBBlobDecryption(record[0], real_key)
            except KeyError:
                passwd = ''
            print ' [-] Create DateTime: %s' % record[1]  # 16byte string
            print ' [-] Last Modified DateTime: %s' % record[2]  # 16byte string
            print ' [-] Description : %s' % record[3]
            print ' [-] Comment : %s' % record[4]
            print ' [-] Creator : %s' % record[5]
            print ' [-] Type : %s' % record[6]
            print ' [-] PrintName : %s' % record[7]
            print ' [-] Alias : %s' % record[8]
            print ' [-] Protected : %s' % record[9]
            print ' [-] Account : %s' % record[10]
            print ' [-] SecurityDomain : %s' % record[11]
            print ' [-] Server : %s' % record[12]
            try:
                print ' [-] Protocol Type : %s' % PROTOCOL_TYPE[record[13]]
            except KeyError:
                print ' [-] Protocol Type : %s' % record[13]
            try:
                print ' [-] Auth Type : %s' % AUTH_TYPE[record[14]]
            except KeyError:
                print ' [-] Auth Type : %s' % record[14]
            print ' [-] Port : %d' % record[15]
            print ' [-] Path : %s' % record[16]
            print ' [-] Password'
            hexdump(passwd)
            print ''

    except KeyError:
        print '[!] Internet Password Table is not available'
        pass

    try:
        TableMetadata, applesharepw_list = keychain.getTable(TableList[tableEnum[CSSM_DL_DB_RECORD_APPLESHARE_PASSWORD]])

        for applesharepw in applesharepw_list:
            record = keychain.getAppleshareRecord(TableList[tableEnum[CSSM_DL_DB_RECORD_APPLESHARE_PASSWORD]], applesharepw)
            print '[+] AppleShare Record (no more used OS X)'
            try:
                real_key = key_list[record[0][0:20]]
                passwd = keychain.DBBlobDecryption(record[0], real_key)
            except KeyError:
                passwd = ''
            #print ''
            print ' [-] Create DateTime: %s' % record[1]  # 16byte string
            print ' [-] Last Modified DateTime: %s' % record[2]  # 16byte string
            print ' [-] Description : %s' % record[3]
            print ' [-] Comment : %s' % record[4]
            print ' [-] Creator : %s' % record[5]
            print ' [-] Type : %s' % record[6]
            print ' [-] PrintName : %s' % record[7]
            print ' [-] Alias : %s' % record[8]
            print ' [-] Protected : %s' % record[9]
            print ' [-] Account : %s' % record[10]
            print ' [-] Volume : %s' % record[11]
            print ' [-] Server : %s' % record[12]
            try:
                print ' [-] Protocol Type : %s' % PROTOCOL_TYPE[record[13]]
            except KeyError:
                print ' [-] Protocol Type : %s' % record[13]
            print ' [-] Address : %d' % record[14]
            print ' [-] Signature : %s' % record[15]
            print ' [-] Password'
            hexdump(passwd)
            print ''

    except KeyError:
        print '[!] AppleShare Table is not available'
        pass

    try:
        TableMetadata, x509CertList = keychain.getTable(TableList[tableEnum[CSSM_DL_DB_RECORD_X509_CERTIFICATE]])

        for x509Cert in x509CertList:
            record = keychain.getx509Record(TableList[tableEnum[CSSM_DL_DB_RECORD_X509_CERTIFICATE]], x509Cert)
            print ' [-] Cert Type: %s' %CERT_TYPE[record[0]]
            print ' [-] Cert Encoding: %s' %CERT_ENCODING[record[1]]
            print ' [-] PrintName : %s' % record[2]
            print ' [-] Alias : %s' % record[3]
            print ' [-] Subject'
            hexdump(record[4])
            print ' [-] Issuer :'
            hexdump(record[5])
            print ' [-] SerialNumber'
            hexdump(record[6])
            print ' [-] SubjectKeyIdentifier'
            hexdump(record[7])
            print ' [-] Public Key Hash'
            hexdump(record[8])
            print ' [-] Certificate'
            hexdump(record[9])
            print ''

    except KeyError:
        print '[!] Certification Table is not available'
        pass

    try:
        TableMetadata, PublicKeyList = keychain.getTable(TableList[tableEnum[CSSM_DL_DB_RECORD_PUBLIC_KEY]])
        for PublicKey in PublicKeyList:
            record = keychain.getKeyRecord(TableList[tableEnum[CSSM_DL_DB_RECORD_PUBLIC_KEY]], PublicKey)
            print '[+] Public Key Record'
            print ' [-] PrintName: %s' %record[0]
            print ' [-] Label'
            hexdump(record[1])
            print ' [-] Key Class : %s'%KEY_TYPE[record[2]]
            print ' [-] Private : %d'%record[3]
            print ' [-] Key Type : %s'%CSSM_ALGORITHMS[record[4]]
            print ' [-] Key Size : %d bits'%record[5]
            print ' [-] Effective Key Size : %d bits'%record[6]
            print ' [-] Extracted : %d'%record[7]
            print ' [-] CSSM Type : %s' %STD_APPLE_ADDIN_MODULE[record[8]]
            print ' [-] Public Key'
            hexdump(record[10])

    except KeyError:
        print '[!] Public Key Table is not available'
        pass

    try:
        table_meta, PrivateKeyList = keychain.getTable(TableList[tableEnum[CSSM_DL_DB_RECORD_PRIVATE_KEY]])
        for PrivateKey in PrivateKeyList:
            record = keychain.getKeyRecord(TableList[tableEnum[CSSM_DL_DB_RECORD_PRIVATE_KEY]], PrivateKey)
            print '[+] Private Key Record'
            print ' [-] PrintName: %s' % record[0]
            print ' [-] Label'
            hexdump(record[1])
            print ' [-] Key Class : %s' % KEY_TYPE[record[2]]
            print ' [-] Private : %d' % record[3]
            print ' [-] Key Type : %s' % CSSM_ALGORITHMS[record[4]]
            print ' [-] Key Size : %d bits' % record[5]
            print ' [-] Effective Key Size : %d bits' % record[6]
            print ' [-] Extracted : %d' % record[7]
            print ' [-] CSSM Type : %s' % STD_APPLE_ADDIN_MODULE[record[8]]
            keyname, privatekey = keychain.PrivateKeyDecryption(record[10], record[9], dbkey)
            print ' [-] Key Name'
            hexdump(keyname)
            print ' [-] Decrypted Private Key'
            hexdump(privatekey)

    except KeyError:
        print '[!] Private Key Table is not available'
        pass

    exit()


if __name__ == "__main__":
    main()
