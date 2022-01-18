# Copyright (c) 2021, ZIH,
# Technische Universitaet Dresden,
# Federal Republic of Germany
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of metricq nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from attr import dataclass
from typing import cast

from . import database as db
from . import document
from .typing import JsonDict


@dataclass
class BaseChangeEvent:
    json: JsonDict

    @property
    def id(self) -> str:
        return cast(str, self.json["id"])

    @property
    def rev(self) -> str:
        return cast(str, self.json["changes"][0]["rev"])

    @property
    def sequence(self) -> str:
        return cast(str, self.json["seq"])


class DeletedEvent(BaseChangeEvent):
    pass


@dataclass
class ChangedEvent(BaseChangeEvent):
    database: "db.Database"

    async def doc(self) -> "document.Document":
        try:
            # if in the request include_docs was given, we can create the
            # document on the spot...
            return document.Document(
                self.database, self.json["doc"]["_id"], self.json["doc"]
            )
        except KeyError:
            # ...otherwise, we fetch the document contents from the server
            return await self.database.get(self.id, rev=self.rev)
