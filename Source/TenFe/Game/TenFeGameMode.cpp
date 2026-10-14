#include "Game/TenFeGameMode.h"

#include "AI/TenFeEnemy.h"
#include "Character/TenFeCharacter.h"
#include "Engine/World.h"
#include "Game/TenFeTrainingDummy.h"

ATenFeGameMode::ATenFeGameMode()
{
    DefaultPawnClass = ATenFeCharacter::StaticClass();
}

void ATenFeGameMode::BeginPlay()
{
    Super::BeginPlay();

    if (UWorld* World = GetWorld())
    {
        World->SpawnActor<ATenFeTrainingDummy>(ATenFeTrainingDummy::StaticClass(), FVector(420.0f, 0.0f, 90.0f), FRotator::ZeroRotator);
        World->SpawnActor<ATenFeEnemy>(ATenFeEnemy::StaticClass(), FVector(650.0f, -260.0f, 100.0f), FRotator::ZeroRotator);
    }
}
