#include <fbow/fbow.h>
#include <fbow/vocabulary_creator.h>

int main(int argc, char** argv)
{
    const cv::Mat allZeroesSources(cv::Mat::zeros(5, 128, CV_32F));

    fbow::Vocabulary vocabulary;
    fbow::VocabularyCreator vocabularyCreator;

    vocabularyCreator.create(vocabulary, allZeroesSources, "", fbow::VocabularyCreator::Params{});

    return 0;
}
