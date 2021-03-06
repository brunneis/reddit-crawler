# Catenae Link
# Copyright (C) 2018 Rodrigo Martínez <dev@brunneis.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

FROM catenae/link:develop

# Topology links
COPY \
    env.py \
    crawler_helper.py \
    submission_crawler.py \
    submission_extractor.py \
    comment_crawler.py \
    stats.py /opt/reddit-crawler/

COPY entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]
